from functools import wraps
from flask import request, jsonify
import logging


class ValidationError(Exception):
    """Exception raised for validation errors"""

    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


class Validator:
    """Base validator class"""

    @staticmethod
    def validate_required(data, fields):
        """Validate that required fields are present and not empty"""
        errors = {}

        for field in fields:
            if field not in data or data[field] is None or data[field] == "":
                errors[field] = f"{field} is required"

        if errors:
            raise ValidationError(errors)

        return True

    @staticmethod
    def validate_type(data, field, expected_type, field_name=None):
        """Validate that a field is of the expected type"""
        field_name = field_name or field

        if field not in data:
            return

        value = data[field]
        if value is not None and not isinstance(value, expected_type):
            raise ValidationError(
                {field: f"{field_name} must be a {expected_type.__name__}"}
            )

        return True

    @staticmethod
    def validate_length(data, field, min_length=None, max_length=None, field_name=None):
        """Validate that a field's length is within specified bounds"""
        field_name = field_name or field

        if field not in data or data[field] is None:
            return

        value = data[field]
        length = len(value)

        if min_length is not None and length < min_length:
            raise ValidationError(
                {field: f"{field_name} must be at least {min_length} characters"}
            )

        if max_length is not None and length > max_length:
            raise ValidationError(
                {field: f"{field_name} must be no more than {max_length} characters"}
            )

        return True

    @staticmethod
    def validate_custom(data, field, validator_func, error_message, field_name=None):
        """Apply a custom validation function to a field"""
        field_name = field_name or field

        if field not in data or data[field] is None:
            return

        value = data[field]
        if not validator_func(value):
            raise ValidationError({field: error_message.format(field_name=field_name)})

        return True


# Decorator for request validation
def validate_request(validator_method):

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger = logging.getLogger(__name__)
            try:
                data = request.get_json()
                if not data:
                    logger.warning("Request validation failed: No JSON data provided")
                    return (
                        jsonify(
                            {
                                "error": "Invalid request format",
                                "details": "Request must contain valid JSON data",
                            }
                        ),
                        422,
                    )

                # Apply the validator
                validator_method(data)

                return f(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"Request validation failed: {e.errors}")
                return jsonify({"error": "Validation error", "details": e.errors}), 422

            except Exception as e:
                logger.error(f"Unexpected error during validation: {str(e)}")
                return jsonify({"error": "Invalid request", "details": str(e)}), 400

        return decorated_function

    return decorator

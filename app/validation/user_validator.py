import re
from .base import Validator, ValidationError


class UserValidator(Validator):
    """Validator for user-related operations"""

    @classmethod
    def validate_registration(cls, data):

        # Check required fields
        cls.validate_required(data, ["username", "password"])

        # Validate username
        cls.validate_length(
            data, "username", min_length=3, max_length=80, field_name="Username"
        )

        # Username must be alphanumeric with underscores
        if "username" in data and data["username"]:
            username = data["username"]
            if not re.match(r"^[a-zA-Z0-9_]+$", username):
                raise ValidationError(
                    {
                        "username": "Username must contain only letters, numbers, and underscores"
                    }
                )

        # Validate password
        cls.validate_length(data, "password", min_length=8, field_name="Password")

        # Password complexity
        if "password" in data and data["password"]:
            password = data["password"]

            # Check for at least one uppercase, one lowercase, and one digit
            if not (
                re.search(r"[A-Z]", password)
                and re.search(r"[a-z]", password)
                and re.search(r"[0-9]", password)
            ):
                raise ValidationError(
                    {
                        "password": "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
                    }
                )

        return True

    @classmethod
    def validate_login(cls, data):

        cls.validate_required(data, ["username", "password"])
        return True

    @classmethod
    def validate_password_change(cls, data):

        cls.validate_required(data, ["current_password", "new_password"])

        # Validate new password
        cls.validate_length(
            data, "new_password", min_length=8, field_name="New password"
        )

        # Password complexity
        if "new_password" in data and data["new_password"]:
            password = data["new_password"]

            # Check for at least one uppercase, one lowercase, and one digit
            if not (
                re.search(r"[A-Z]", password)
                and re.search(r"[a-z]", password)
                and re.search(r"[0-9]", password)
            ):
                raise ValidationError(
                    {
                        "new_password": "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
                    }
                )

        return True

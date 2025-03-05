from .base import Validator, ValidationError


class TextValidator(Validator):

    @classmethod
    def validate_generate_text(cls, data):

        cls.validate_required(data, ["prompt"])
        cls.validate_length(
            data, "prompt", min_length=1, max_length=5000, field_name="Prompt"
        )

        # Validate options if present
        if "options" in data:
            cls.validate_type(data, "options", dict, field_name="Options")

            options = data.get("options", {})

            # Validate temperature if present
            if "temperature" in options:
                temperature = options["temperature"]

                if (
                    not isinstance(temperature, (int, float))
                    or temperature < 0
                    or temperature > 1
                ):
                    raise ValidationError(
                        {
                            "options.temperature": "Temperature must be a number between 0 and 1"
                        }
                    )

            # Validate max_tokens if present
            if "max_tokens" in options:
                max_tokens = options["max_tokens"]

                if not isinstance(max_tokens, int) or max_tokens < 1:
                    raise ValidationError(
                        {"options.max_tokens": "Max tokens must be a positive integer"}
                    )

        return True

    @classmethod
    def validate_update_text(cls, data):

        if not data:
            raise ValidationError({"data": "No data provided"})

        if "prompt" not in data and "response" not in data:
            raise ValidationError(
                {
                    "prompt/response": "At least one of 'prompt' or 'response' must be provided"
                }
            )

        if "prompt" in data:
            cls.validate_length(
                data, "prompt", min_length=1, max_length=5000, field_name="Prompt"
            )

        if "response" in data:
            cls.validate_length(data, "response", min_length=1, field_name="Response")

        return True

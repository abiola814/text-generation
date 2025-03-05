import os
import openai
from .base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI implementation of AIProvider"""

    def __init__(self, api_key=None, model=None):
        super().__init__()
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

        # Set the API key for the openai library
        openai.api_key = self.api_key

        # Clear any proxy environment variables that might interfere
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)

        self.logger.info(f"Initialized OpenAI provider with model: {self.model}")

    def generate_text(self, prompt, options=None):

        options = options or {}

        try:
            response = openai.ChatCompletion.create(
                model=options.get("model", self.model),
                messages=[
                    {
                        "role": "system",
                        "content": options.get(
                            "system_prompt", "You are a helpful assistant."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=options.get("max_tokens", 1000),
                temperature=options.get("temperature", 0.7),
            )

            # Extract the text from the response
            return response["choices"][0]["message"]["content"]

        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate text with OpenAI: {str(e)}")

    def get_provider_name(self):
        """Return the provider name"""
        return "OpenAI"

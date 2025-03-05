from abc import ABC, abstractmethod
import logging


class AIProvider(ABC):
    """Base class for AI text generation providers"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def generate_text(self, prompt, options=None):
        pass

    @abstractmethod
    def get_provider_name(self):
        # working on it
        pass

    def generate_with_logging(self, prompt, options=None):

        options = options or {}
        provider_name = self.get_provider_name()

        truncated_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
        self.logger.info(
            f"Generating text with {provider_name}. Prompt: {truncated_prompt}"
        )

        try:
            response = self.generate_text(prompt, options)
            response_length = len(response)

            self.logger.info(
                f"{provider_name} text generation successful. Response length: {response_length}"
            )
            return response

        except Exception as e:
            self.logger.error(f"{provider_name} API error: {str(e)}")
            raise Exception(f"Failed to generate text with {provider_name}: {str(e)}")

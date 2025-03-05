import os
import logging
from .factory import AIProviderFactory


class AIService:
    """Service for generating text using AI providers"""

    def __init__(self, provider_name=None, **provider_options):

        self.logger = logging.getLogger(__name__)

        # Default to environment variable or 'openai'
        self.provider_name = provider_name or os.environ.get("AI_PROVIDER", "openai")

        # Get the provider from the factory
        self.provider = AIProviderFactory.get_provider(
            self.provider_name, **provider_options
        )

        self.logger.info(
            f"AI Service initialized with provider: {self.provider.get_provider_name()}"
        )

    def generate_text(self, prompt, options=None):

        return self.provider.generate_with_logging(prompt, options)

    def get_provider_name(self):

        return self.provider.get_provider_name()

import logging
from .providers.openai_provider import OpenAIProvider

# Add imports for other providers here as they are implemented
# from .providers.claude_provider import ClaudeProvider


class AIProviderFactory:
    """Factory for creating AI providers"""

    @staticmethod
    def get_provider(provider_name, **kwargs):

        logger = logging.getLogger(__name__)

        # Map of available providers
        providers = {
            "openai": OpenAIProvider,
            # Add more providers here as they are implemented
            # 'claude': DeepSeekProvider,
        }

        provider_name = provider_name.lower()
        provider_class = providers.get(provider_name)

        if not provider_class:
            logger.error(f"Unknown AI provider requested: {provider_name}")
            raise ValueError(f"Unknown AI provider: {provider_name}")

        logger.info(f"Creating {provider_name} provider")
        return provider_class(**kwargs)

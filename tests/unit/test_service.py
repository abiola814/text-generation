import pytest
from unittest.mock import MagicMock, patch
from app.service.ai_service import AIService
from app.service.providers.base import AIProvider
from app.service.factory import AIProviderFactory


class MockProvider(AIProvider):
    """Mock AI provider for testing"""

    def __init__(self, response_text="Mock response"):
        super().__init__()
        self.response_text = response_text
        self.generate_text_called = False
        self.last_prompt = None
        self.last_options = None

    def generate_text(self, prompt, options=None):
        self.generate_text_called = True
        self.last_prompt = prompt
        self.last_options = options or {}
        return self.response_text

    def get_provider_name(self):
        return "MockProvider"


class TestAIProviderFactory:
    """Test the AI Provider Factory"""

    def test_get_provider_openai(self):
        """Test getting OpenAI provider"""
        # Use a simpler patching approach
        mock_provider = MagicMock()

        with patch(
            "app.service.factory.OpenAIProvider", return_value=mock_provider
        ) as mock_openai:
            # Directly patch the get_provider method
            with patch.object(
                AIProviderFactory, "get_provider", return_value=mock_provider
            ) as mock_get_provider:
                provider = AIProviderFactory.get_provider("openai")

                assert provider is mock_provider

    def test_get_provider_unknown(self):
        """Test getting unknown provider raises error"""
        with pytest.raises(ValueError) as excinfo:
            AIProviderFactory.get_provider("unknown_provider")

        assert "Unknown AI provider" in str(excinfo.value)

    def test_provider_with_options(self):
        """Test passing options to provider"""
        mock_provider = MagicMock()

        with patch("app.service.factory.OpenAIProvider", return_value=mock_provider):
            with patch.object(
                AIProviderFactory, "get_provider", return_value=mock_provider
            ):
                options = {"api_key": "test_key", "model": "test_model"}
                provider = AIProviderFactory.get_provider("openai", **options)

                assert provider is mock_provider


class TestAIService:
    """Test the AI Service"""

    def test_service_initialization(self):
        """Test initializing the service with default provider"""
        mock_provider = MockProvider()

        # Patch the get_provider method
        with patch.object(
            AIProviderFactory, "get_provider", return_value=mock_provider
        ) as mock_get_provider:
            service = AIService()

            mock_get_provider.assert_called_once()
            assert service.provider is mock_provider

    def test_service_with_specific_provider(self):
        """Test initializing the service with a specific provider"""
        mock_provider = MockProvider()

        # Patch the get_provider method
        with patch.object(
            AIProviderFactory, "get_provider", return_value=mock_provider
        ) as mock_get_provider:
            service = AIService(provider_name="test-provider")

            mock_get_provider.assert_called_once_with("test-provider")
            assert service.provider is mock_provider

    def test_generate_text(self):
        """Test generating text through the service"""
        mock_provider = MockProvider("AI generated response")

        with patch.object(
            AIProviderFactory, "get_provider", return_value=mock_provider
        ):
            service = AIService()
            response = service.generate_text("Generate some text")

            assert response == "AI generated response"
            assert mock_provider.generate_text_called
            assert mock_provider.last_prompt == "Generate some text"

    def test_get_provider_name(self):
        """Test getting the provider name from the service"""
        mock_provider = MockProvider()

        with patch.object(
            AIProviderFactory, "get_provider", return_value=mock_provider
        ):
            service = AIService()
            provider_name = service.get_provider_name()

            assert provider_name == "MockProvider"

    def test_generate_with_options(self):
        """Test generating text with options"""
        mock_provider = MockProvider("Response with options")

        with patch.object(
            AIProviderFactory, "get_provider", return_value=mock_provider
        ):
            service = AIService()
            options = {"temperature": 0.8, "max_tokens": 500}
            response = service.generate_text("Generate with options", options)

            assert response == "Response with options"
            assert mock_provider.generate_text_called
            assert mock_provider.last_prompt == "Generate with options"
            assert mock_provider.last_options.get("temperature") == 0.8
            assert mock_provider.last_options.get("max_tokens") == 500

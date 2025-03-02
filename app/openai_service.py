import os
from flask import current_app
import openai

class OpenAIService:
    def __init__(self, api_key=None, model=None):
        # Set API key and model
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model or os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

        # Clear any proxy environment variables that might interfere
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        # Set the API key for the openai library
        openai.api_key = self.api_key

    def generate_text(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            # Extract the text from the response (different structure in older versions)
            return response['choices'][0]['message']['content']
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate text: {str(e)}")
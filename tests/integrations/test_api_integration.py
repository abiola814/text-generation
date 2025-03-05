import pytest
import json
from unittest.mock import patch
from app.models import GeneratedText


class TestApiEndpoints:
    """Test API endpoints"""
    
    @patch('app.service.ai_service.AIService.generate_text')
    def test_generate_text(self, mock_generate, client, auth_headers):
        """Test generating text"""
        # Mock the AI service response
        mock_generate.return_value = "AI generated response"
        
        # Make the request
        data = {'prompt': 'Test prompt'}
        response = client.post(
            '/api/generate-text',
            data=json.dumps(data),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['prompt'] == 'Test prompt'
        assert response_data['response'] == 'AI generated response'
        
        # Verify AI service was called
        mock_generate.assert_called_once_with(prompt='Test prompt')
    
    def test_generate_text_unauthorized(self, client):
        """Test generating text without authentication"""
        # Make the request without auth headers
        data = {'prompt': 'Test prompt'}
        response = client.post(
            '/api/generate-text',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Check response - should indicate unauthorized
        assert response.status_code == 401
    
    def test_get_generated_text(self, client, session, test_user, auth_headers):
        """Test retrieving a generated text by ID"""
        # Create a test text
        text = GeneratedText(
            user_id=test_user.id,
            prompt="Test prompt",
            response="Test response"
        )
        session.add(text)
        session.commit()
        
        # Make the request
        response = client.get(
            f'/api/generated-text/{text.id}',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['id'] == text.id
        assert response_data['prompt'] == "Test prompt"
        assert response_data['response'] == "Test response"
        assert response_data['user_id'] == test_user.id
    
    def test_get_text_not_found(self, client, auth_headers):
        """Test retrieving a non-existent text"""
        # Make the request with non-existent ID
        response = client.get(
            '/api/generated-text/9999',
            headers=auth_headers
        )
        
        # Check response - should indicate not found
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_update_text(self, client, session, test_user, auth_headers):
        """Test updating a generated text"""
        # Create a test text
        text = GeneratedText(
            user_id=test_user.id,
            prompt="Original prompt",
            response="Original response"
        )
        session.add(text)
        session.commit()
        
        # Make the update request
        update_data = {
            'prompt': 'Updated prompt',
            'response': 'Updated response'
        }
        response = client.put(
            f'/api/generated-text/{text.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['prompt'] == 'Updated prompt'
        assert response_data['response'] == 'Updated response'
        
        # Verify database update
        updated_text = session.query(GeneratedText).get(text.id)
        assert updated_text.prompt == 'Updated prompt'
        assert updated_text.response == 'Updated response'
    
    def test_update_text_partial(self, client, session, test_user, auth_headers):
        """Test partial update of a generated text"""
        # Create a test text
        text = GeneratedText(
            user_id=test_user.id,
            prompt="Original prompt",
            response="Original response"
        )
        session.add(text)
        session.commit()
        
        # Make the update request - only update prompt
        update_data = {'prompt': 'Only prompt updated'}
        response = client.put(
            f'/api/generated-text/{text.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['prompt'] == 'Only prompt updated'
        assert response_data['response'] == 'Original response'  # Unchanged
    
    def test_delete_text(self, client, session, test_user, auth_headers):
        """Test deleting a generated text"""
        # Create a test text
        text = GeneratedText(
            user_id=test_user.id,
            prompt="Delete me",
            response="Delete response"
        )
        session.add(text)
        session.commit()
        
        text_id = text.id
        
        # Make the delete request
        response = client.delete(
            f'/api/generated-text/{text_id}',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'deleted' in response_data['message'].lower()
        
        # Verify deletion in database
        deleted_text = session.query(GeneratedText).get(text_id)
        assert deleted_text is None
    
    def test_get_all_texts(self, client, session, test_user, auth_headers):
        """Test retrieving all generated texts for a user"""
        # Create multiple test texts
        texts = [
            GeneratedText(
                user_id=test_user.id,
                prompt=f"Prompt {i}",
                response=f"Response {i}"
            )
            for i in range(3)
        ]
        session.add_all(texts)
        session.commit()
        
        # Make the request
        response = client.get(
            '/api/generated-texts',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)
        assert len(response_data) == 3
        assert all(text['user_id'] == test_user.id for text in response_data)

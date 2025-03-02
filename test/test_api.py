# test_api.py
import pytest
import json
from unittest.mock import patch, MagicMock
from app.models import GeneratedText, db

# Tests for /generate-text endpoint
def test_generate_text_success(client, auth_header, mock_openai_service, test_user_id):
    """Test successful text generation."""
    response = client.post(
        '/api/generate-text',
        headers=auth_header,
        data=json.dumps({'prompt': 'Test prompt'}),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['prompt'] == 'Test prompt'
    assert data['response'] == 'This is a mocked response from OpenAI.'
    assert data['user_id'] == test_user_id
    mock_openai_service.return_value.generate_text.assert_called_once_with(prompt='Test prompt')

def test_generate_text_missing_prompt(client, auth_header):
    """Test text generation with missing prompt."""
    response = client.post(
        '/api/generate-text',
        headers=auth_header,
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing prompt'

def test_generate_text_service_error(client, auth_header, mock_openai_service):
    """Test text generation when OpenAI service raises an exception."""
    mock_openai_service.return_value.generate_text.side_effect = Exception("API Error")
    
    response = client.post(
        '/api/generate-text',
        headers=auth_header,
        data=json.dumps({'prompt': 'Test prompt'}),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    assert 'error' in json.loads(response.data)

def test_generate_text_unauthorized(client):
    """Test text generation without authentication."""
    response = client.post(
        '/api/generate-text',
        data=json.dumps({'prompt': 'Test prompt'}),
        content_type='application/json'
    )
    
    assert response.status_code == 401

# Tests for /generated-text/<id> GET endpoint
def test_get_generated_text_success(client, auth_header, create_text, test_user_id):
    """Test retrieving a specific generated text."""
    # Create a test generated text
    text_id = create_text(user_id=test_user_id)
    
    response = client.get(
        f'/api/generated-text/{text_id}',
        headers=auth_header
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['prompt'] == 'Test prompt'
    assert data['response'] == 'Test response'
    assert data['user_id'] == test_user_id

def test_get_generated_text_not_found(client, auth_header):
    """Test retrieving a non-existent generated text."""
    response = client.get(
        '/api/generated-text/9999',
        headers=auth_header
    )
    
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)

def test_get_generated_text_unauthorized_access(client, auth_header, app, create_text):
    """Test retrieving another user's generated text."""
    # Create a text for another user (ID: 999)
    text_id = create_text(user_id=999)
    
    response = client.get(
        f'/api/generated-text/{text_id}',
        headers=auth_header
    )
    
    # Should be 403 or 404 depending on your API's behavior for unauthorized access
    assert response.status_code in (403, 404)
    assert 'error' in json.loads(response.data)

# Tests for /generated-text/<id> PUT endpoint
def test_update_generated_text_success(client, auth_header, create_text, test_user_id):
    """Test updating a generated text."""
    # Create a test generated text
    text_id = create_text(user_id=test_user_id, prompt="Original prompt", response="Original response")
    
    response = client.put(
        f'/api/generated-text/{text_id}',
        headers=auth_header,
        data=json.dumps({'prompt': 'Updated prompt', 'response': 'Updated response'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['prompt'] == 'Updated prompt'
    assert data['response'] == 'Updated response'
    assert data['user_id'] == test_user_id

def test_update_generated_text_partial(client, auth_header, create_text, test_user_id):
    """Test partially updating a generated text."""
    # Create a test generated text
    text_id = create_text(user_id=test_user_id, prompt="Original prompt", response="Original response")
    
    response = client.put(
        f'/api/generated-text/{text_id}',
        headers=auth_header,
        data=json.dumps({'prompt': 'Updated prompt only'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['prompt'] == 'Updated prompt only'
    assert data['response'] == 'Original response'  # Should remain unchanged
    assert data['user_id'] == test_user_id

def test_update_generated_text_not_found(client, auth_header):
    """Test updating a non-existent generated text."""
    response = client.put(
        '/api/generated-text/9999',
        headers=auth_header,
        data=json.dumps({'prompt': 'Updated prompt', 'response': 'Updated response'}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)

def test_update_generated_text_no_data(client, auth_header, create_text, test_user_id):
    """Test updating a generated text with no data."""
    # Create a test generated text
    text_id = create_text(user_id=test_user_id)
    
    response = client.put(
        f'/api/generated-text/{text_id}',
        headers=auth_header,
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

# Tests for /generated-text/<id> DELETE endpoint
def test_delete_generated_text_success(client, auth_header, create_text, test_user_id, app):
    """Test deleting a generated text."""
    # Create a test generated text
    text_id = create_text(user_id=test_user_id)
    
    response = client.delete(
        f'/api/generated-text/{text_id}',
        headers=auth_header
    )
    
    assert response.status_code == 200
    assert 'message' in json.loads(response.data)
    
    # Verify it's actually gone
    with app.app_context():
        assert GeneratedText.query.get(text_id) is None

def test_delete_generated_text_not_found(client, auth_header):
    """Test deleting a non-existent generated text."""
    response = client.delete(
        '/api/generated-text/9999',
        headers=auth_header
    )
    
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)

# Tests for /generated-texts GET endpoint
def test_get_all_generated_texts_success(client, auth_header, create_text, test_user_id):
    """Test retrieving all generated texts for a user."""
    # Create a few test generated texts
    for i in range(3):
        create_text(user_id=test_user_id, prompt=f"Test prompt {i}", response=f"Test response {i}")
    
    response = client.get(
        '/api/generated-texts',
        headers=auth_header
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Handle different response formats
    if isinstance(data, dict) and 'generated_texts' in data:
        texts = data['generated_texts']
        assert len(texts) >= 3
        assert 'count' in data
        assert data['count'] >= 3
    else:
        # Assume it's a list directly
        assert len(data) >= 3
    
    # Check if texts are for the correct user
    if isinstance(data, dict) and 'generated_texts' in data:
        for text in data['generated_texts']:
            assert text['user_id'] == test_user_id
    else:
        for text in data:
            assert text['user_id'] == test_user_id

def test_get_all_generated_texts_empty(client, auth_header):
    """Test retrieving all generated texts when there are none."""
    # No texts created - the fixture auto-clears between tests
    
    response = client.get(
        '/api/generated-texts',
        headers=auth_header
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Handle different response formats
    if isinstance(data, dict) and 'generated_texts' in data:
        assert data['generated_texts'] == []
        assert data['count'] == 0
    else:
        # Assume it's a list directly
        assert data == []
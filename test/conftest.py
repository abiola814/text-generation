# conftest.py
import pytest
import json
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.models import db, User, GeneratedText
from unittest.mock import patch

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing - session scope means it runs once for all tests."""
    app = Flask(__name__)
    app.config.from_object('app.config.TestingConfig')
    
    # Make sure SQLite doesn't use memory for session scope
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    # Configure JWT for testing
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Don't expire tokens in tests
    

    jwt = JWTManager(app)
    
    # Import blueprints 
    from app.auth import auth_bp
    from app.routes import api_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create app context that stays active for all tests
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
        # Clean up any existing test users first (in case of previous failed tests)
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create a permanent test user for the entire test session
        test_user = User(username='testuser')
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        
        # Store the user_id for later use
        app.config['TEST_USER_ID'] = test_user.id
        
        yield app
        
        # Cleanup whem all tests have completed
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()

@pytest.fixture
def test_user_id(app):
    """Return the test user ID that was created in the app fixture."""
    return app.config['TEST_USER_ID']

@pytest.fixture
def auth_header(app):
    """Create authentication header with JWT token for test user."""
    user_id = app.config['TEST_USER_ID']
    access_token = create_access_token(identity=str(user_id))
    
    # authentication
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def mock_openai_service():
    """Mock the OpenAI service for testing."""
    with patch('app.routes.OpenAIService') as mock:
        # Configure the mock to return a predictable response
        mock_instance = mock.return_value
        mock_instance.generate_text.return_value = 'This is a mocked response from OpenAI.'
        yield mock

# Helper function to create test text
def create_test_text(app, user_id, prompt="Test prompt", response="Test response"):
    with app.app_context():
        test_text = GeneratedText(
            user_id=user_id,
            prompt=prompt,
            response=response
        )
        db.session.add(test_text)
        db.session.commit()
        return test_text.id

# Update create_test_text to be a fixture for easier use in tests
@pytest.fixture
def create_text(app):
    def _create_text(user_id=None, prompt="Test prompt", response="Test response"):
        if user_id is None:
            user_id = app.config['TEST_USER_ID']
        return create_test_text(app, user_id, prompt, response)
    return _create_text

# Clear generated texts between tests to avoid interference
@pytest.fixture(autouse=True)
def clear_generated_texts(app):
    with app.app_context():
        yield
        # After each test, delete all generated texts
        GeneratedText.query.delete()
        db.session.commit()
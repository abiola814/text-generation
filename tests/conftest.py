import os
import pytest
import uuid
from app import create_app
from app.models import db as _db
from app.config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing"""
    # Set testing environment variables
    os.environ["FLASK_ENV"] = "testing"

    # Create the app with testing config
    test_app = create_app(TestingConfig)

    # Create testing context
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="session")
def db(app):
    """Initialize and provide the database"""
    # Create the database and tables
    _db.drop_all()  # First drop all tables to ensure clean state
    _db.create_all()

    yield _db

    # Teardown - drop all tables
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Provide a function-scoped session for tests"""
    # Begin a transaction
    connection = db.engine.connect()
    transaction = connection.begin()

    # Use the session with the started transaction
    session = db.session

    # Set the session's connection
    session.configure(bind=connection)

    yield session

    # Rollback the transaction after the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app):
    """Provide a test client for testing flask routes"""
    return app.test_client()


@pytest.fixture
def test_user(session):
    """Create a test user for authentication tests with unique username"""
    from app.models import User

    # Generate a unique username to avoid conflicts
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"

    user = User(username=unique_username)
    user.set_password("password123")
    session.add(user)
    session.commit()

    return user


@pytest.fixture
def auth_token(app, client, test_user):
    """Get authentication token for a test user"""
    from flask_jwt_extended import create_access_token

    with app.app_context():
        return create_access_token(identity=str(test_user.id))


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with authentication"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    """Mock OpenAI API calls to avoid quota issues"""

    class MockChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "This is a mocked response from OpenAI",
                            "role": "assistant",
                        }
                    }
                ]
            }

    class MockOpenAI:
        api_key = "sk-mock-key"
        ChatCompletion = MockChatCompletion

    # Patch the openai module
    monkeypatch.setattr("app.service.providers.openai_provider.openai", MockOpenAI)

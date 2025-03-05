import pytest
from datetime import datetime
from app.models import User, GeneratedText


class TestUserModel:
    """Test the User model"""

    def test_user_creation(self, session):
        """Test creating a new user"""
        user = User(username="testuser123")
        user.set_password("securepassword")

        session.add(user)
        session.commit()

        # Query the user
        queried_user = session.query(User).filter_by(username="testuser123").first()

        assert queried_user is not None
        assert queried_user.username == "testuser123"
        assert queried_user.check_password("securepassword") is True
        assert queried_user.check_password("wrongpassword") is False
        assert isinstance(queried_user.created_at, datetime)

    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = User(username="passworduser")
        password = "mysecretpassword"
        user.set_password(password)

        # Password should be hashed, not stored in plaintext
        assert user.password_hash != password
        assert user.check_password(password) is True

    def test_user_representation(self):
        """Test the string representation of a user"""
        user = User(username="repuser")
        assert str(user) == "<User repuser>"


class TestGeneratedTextModel:
    """Test the GeneratedText model"""

    def test_text_creation(self, session, test_user, monkeypatch):
        """Test creating a new generated text"""
        # First, make sure we have the correct user_id
        current_user = session.query(User).filter_by(id=test_user.id).first()
        assert current_user is not None, "Test user not found in database"

        # Get a fresh queried user from the database to avoid any session issues
        user_id = current_user.id

        # Create generated text with the known user ID
        expected_response = "AI generated response"

        # Delete any existing test data
        session.query(GeneratedText).filter_by(prompt="Test prompt").delete()
        session.commit()

        # Create a new text entry
        text = GeneratedText(
            user_id=user_id,
            prompt="Test prompt",
            response=expected_response,
            provider="openai",  # Note: case sensitive match with the database schema
        )

        session.add(text)
        session.commit()

        # Query the text
        queried_text = (
            session.query(GeneratedText).filter_by(prompt="Test prompt").first()
        )

        assert queried_text is not None, "Could not find the created text"
        assert queried_text.prompt == "Test prompt"
        assert queried_text.response == expected_response
        assert queried_text.provider == "openai"
        assert (
            queried_text.user_id == user_id
        ), f"User ID mismatch: expected {user_id}, got {queried_text.user_id}"
        assert isinstance(queried_text.timestamp, datetime)

    def test_text_to_dict(self, test_user):
        """Test the to_dict method of GeneratedText"""
        text = GeneratedText(
            id=1,
            user_id=test_user.id,
            prompt="Convert to dict",
            response="Dictionary response",
            provider="openai",
        )

        # Set a specific timestamp for testing
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        text.timestamp = fixed_time

        # Convert to dictionary
        result = text.to_dict()

        assert result["id"] == 1
        assert result["user_id"] == test_user.id
        assert result["prompt"] == "Convert to dict"
        assert result["response"] == "Dictionary response"
        assert result["provider"] == "openai"
        assert result["timestamp"] == fixed_time.isoformat()

    def test_text_representation(self, test_user):
        """Test the string representation of a generated text"""
        text = GeneratedText(
            id=42, user_id=test_user.id, prompt="Test", response="Response"
        )
        assert str(text) == "<GeneratedText 42>"

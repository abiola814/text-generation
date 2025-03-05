import pytest
import json
from flask import url_for
from app.models import User


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_success(self, client, session):
        """Test successful user registration"""
        # Register user
        data = {"username": "newuser", "password": "Password123"}

        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        # Check response
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert "message" in response_data
        assert response_data["message"] == "User registered successfully"

        # Verify user was created in database
        user = session.query(User).filter_by(username="newuser").first()
        assert user is not None

    def test_register_duplicate(self, client, test_user):
        """Test registration with duplicate username"""
        # Try to register with existing username
        data = {
            "username": test_user.username,  # Already exists
            "password": "Password123",
        }

        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        # Check response - should indicate conflict
        assert response.status_code == 409
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "exists" in response_data["error"].lower()

    def test_register_validation_error(self, client):
        """Test registration with invalid data"""
        # Missing password
        data = {"username": "validuser"}

        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        # Check response - should indicate validation error
        assert response.status_code == 422
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "details" in response_data
        assert "password" in response_data["details"]

    def test_login_success(self, client, test_user):
        """Test successful login"""
        # Login with valid credentials
        data = {
            "username": test_user.username,
            "password": "password123",  # Set in the test_user fixture
        }

        response = client.post(
            "/auth/login", data=json.dumps(data), content_type="application/json"
        )

        # Check response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert "access_token" in response_data
        assert response_data["access_token"] is not None

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        # Login with wrong password
        data = {"username": test_user.username, "password": "wrong_password"}

        response = client.post(
            "/auth/login", data=json.dumps(data), content_type="application/json"
        )

        # Check response - should indicate unauthorized
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "error" in response_data
        assert "invalid" in response_data["error"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        # Login with non-existent username
        data = {"username": "nonexistent_user", "password": "password123"}

        response = client.post(
            "/auth/login", data=json.dumps(data), content_type="application/json"
        )

        # Check response - should indicate unauthorized
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert "error" in response_data

    def test_login_case_insensitive(self, client, test_user):
        """Test login with case-insensitive username"""
        # Login with uppercase username
        data = {
            "username": test_user.username.upper(),
            "password": "password123",  # Set in the test_user fixture
        }

        response = client.post(
            "/auth/login", data=json.dumps(data), content_type="application/json"
        )

        # Check response - should succeed
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert "access_token" in response_data

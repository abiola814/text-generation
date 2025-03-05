import pytest
import json
from unittest.mock import patch


class TestFullWorkflow:
    """Test end-to-end user workflows"""

    @patch("app.service.ai_service.AIService.generate_text")
    def test_user_full_workflow(self, mock_generate, client, session):
        """Test a complete user workflow: register, login, generate text, retrieve, update, delete"""
        mock_generate.return_value = "AI generated response"

        # user Register
        register_data = {"username": "workflow_user", "password": "Password123"}
        register_response = client.post(
            "/auth/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )
        assert register_response.status_code == 201

        # new Login user
        login_data = {"username": "workflow_user", "password": "Password123"}
        login_response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )
        assert login_response.status_code == 200

        # Get the token
        login_data = json.loads(login_response.data)
        token = login_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Generate text
        generate_data = {"prompt": "Workflow test prompt"}
        generate_response = client.post(
            "/api/generate-text",
            data=json.dumps(generate_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert generate_response.status_code == 201

        # Get text ID
        text_data = json.loads(generate_response.data)
        text_id = text_data["id"]

        # Retrieve the generated text
        get_response = client.get(
            f"/api/generated-text/{text_id}", headers=auth_headers
        )
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert get_data["prompt"] == "Workflow test prompt"
        assert get_data["response"] == "AI generated response"

        # Update the text
        update_data = {"prompt": "Updated workflow prompt"}
        update_response = client.put(
            f"/api/generated-text/{text_id}",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        update_data = json.loads(update_response.data)
        assert update_data["prompt"] == "Updated workflow prompt"

        # Retrieve all texts
        get_all_response = client.get("/api/generated-texts", headers=auth_headers)
        assert get_all_response.status_code == 200
        all_texts = json.loads(get_all_response.data)
        assert len(all_texts) == 1
        assert all_texts[0]["id"] == text_id

        # Delete the text
        delete_response = client.delete(
            f"/api/generated-text/{text_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

        # Verify deletion by trying to retrieve it
        verify_response = client.get(
            f"/api/generated-text/{text_id}", headers=auth_headers
        )
        assert verify_response.status_code == 404

    @patch("app.service.ai_service.AIService.generate_text")
    def test_provider_selection(self, mock_generate, client, auth_headers):
        """Test generating text with different AI providers"""
        mock_generate.return_value = "Response from selected provider"

        # Test the default provider
        data = {"prompt": "Default provider test"}
        response1 = client.post(
            "/api/generate-text",
            data=json.dumps(data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response1.status_code == 201

        data = {"prompt": "Specific provider test"}
        response2 = client.post(
            "/api/generate-text?provider=openai",
            data=json.dumps(data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response2.status_code == 201

        # Both providers should work (testing the provider pattern)
        assert (
            json.loads(response1.data)["response"] == "Response from selected provider"
        )
        assert (
            json.loads(response2.data)["response"] == "Response from selected provider"
        )

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

import pytest
from fastapi.testclient import TestClient

class TestIntegrationScenarios:
    """Integration tests for complete user workflows."""
    
    def test_complete_user_workflow(self, client):
        """Test complete user registration, login, and data access workflow."""
        # 1. Register a user
        user_data = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Software Engineer",
            "password": "IntegrationTest123!"
        }
        
        register_response = client.post("/users", json=user_data)
        assert register_response.status_code == 201
        created_user = register_response.json()
        user_id = created_user["id"]
        
        # 2. Login with the user
        login_response = client.post("/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # 3. Access user's own data
        get_response = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        
        # Verify data consistency
        assert retrieved_user["id"] == user_id
        assert retrieved_user["name"] == user_data["name"]
        assert retrieved_user["email"] == user_data["email"]
        assert retrieved_user["date_of_birth"] == user_data["date_of_birth"]
        assert retrieved_user["job_title"] == user_data["job_title"]
        assert retrieved_user["role"] == "user"
    
    def test_cross_user_access_denied_workflow(self, client):
        """Test that users cannot access each other's data."""
        # Create two users
        user1_data = {
            "name": "User One",
            "email": "user1@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "UserOnePassword123!"
        }
        
        user2_data = {
            "name": "User Two",
            "email": "user2@example.com",
            "date_of_birth": "1995-05-15",
            "job_title": "Designer",
            "password": "UserTwoPassword456!"
        }
        
        # Register both users
        user1_response = client.post("/users", json=user1_data)
        assert user1_response.status_code == 201
        user1_id = user1_response.json()["id"]
        
        user2_response = client.post("/users", json=user2_data)
        assert user2_response.status_code == 201
        user2_id = user2_response.json()["id"]
        
        # Login as user 2
        user2_login = client.post("/login", json={
            "email": user2_data["email"],
            "password": user2_data["password"]
        })
        assert user2_login.status_code == 200
        user2_token = user2_login.json()["access_token"]
        
        # User 2 tries to access User 1's data - should be forbidden
        cross_access_response = client.get(
            f"/users/{user1_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert cross_access_response.status_code == 403
        assert "Forbidden" in cross_access_response.json()["detail"]
        
        # User 2 should still be able to access their own data
        self_access_response = client.get(
            f"/users/{user2_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert self_access_response.status_code == 200
        assert self_access_response.json()["id"] == user2_id
    
    def test_password_validation_integration(self, client):
        """Test password validation with various invalid passwords."""
        base_user_data = {
            "name": "Password Test User",
            "email": "passwordtest@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Tester"
        }
        
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigitsHere!",  # No digits
            "NoSymbols123",  # No symbols
            "123456789012",  # Only digits
            "abcdefghijkl",  # Only lowercase
            "ABCDEFGHIJKL",  # Only uppercase
            "!@#$%^&*()_+",  # Only symbols
        ]
        
        for invalid_password in invalid_passwords:
            user_data = {**base_user_data, "password": invalid_password}
            response = client.post("/users", json=user_data)
            assert response.status_code == 422, f"Password '{invalid_password}' should be invalid"
            
            error_detail = response.json()["detail"]
            assert any("password" in str(error).lower() for error in error_detail)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
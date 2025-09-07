import pytest
from fastapi.testclient import TestClient

class TestUserAccess:
    """Test user access control and authorization."""
    
    def test_get_user_self_access(self, client, create_test_user, get_auth_token):
        """Test user can access their own data."""
        user_data = create_test_user
        token = get_auth_token
        
        response = client.get(
            f"/users/{user_data['id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        returned_user = response.json()
        assert returned_user["id"] == user_data["id"]
        assert returned_user["email"] == user_data["email"]
        assert returned_user["name"] == user_data["name"]
        assert returned_user["role"] == "user"
        assert returned_user["date_of_birth"] == user_data["date_of_birth"]
        assert returned_user["job_title"] == user_data["job_title"]
    
    def test_get_user_cross_access_forbidden(self, client, create_test_user, create_test_user_2, get_auth_token_2):
        """Test user cannot access another user's data (HTTP 403)."""
        user1_data = create_test_user
        user2_token = get_auth_token_2
        
        # User 2 tries to access User 1's data
        response = client.get(
            f"/users/{user1_data['id']}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]
    
    def test_get_user_unauthorized(self, client, create_test_user):
        """Test accessing user data without authentication fails."""
        user_data = create_test_user
        
        response = client.get(f"/users/{user_data['id']}")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_user_invalid_token(self, client, create_test_user):
        """Test accessing user data with invalid token fails."""
        user_data = create_test_user
        
        response = client.get(
            f"/users/{user_data['id']}",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_get_user_nonexistent(self, client, get_admin_token):
        """Test accessing non-existent user returns 404."""
        token = get_admin_token
        print (token)
        
        response = client.get(
            "/users/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_user_malformed_user_id(self, client, get_auth_token):
        """Test accessing user with malformed ID returns 422."""
        token = get_auth_token
        
        response = client.get(
            "/users/invalid_id",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422
    
    def test_admin_can_access_any_user(self, client, create_test_user, get_admin_token):
        """Test admin user can access any user's data."""
        user_data = create_test_user
        admin_token = get_admin_token
        
        # Admin tries to access regular user's data
        response = client.get(
            f"/users/{user_data['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        returned_user = response.json()
        assert returned_user["id"] == user_data["id"]
        assert returned_user["email"] == user_data["email"]
        assert returned_user["name"] == user_data["name"]
        assert returned_user["role"] == "user"
        assert returned_user["date_of_birth"] == user_data["date_of_birth"]
        assert returned_user["job_title"] == user_data["job_title"]
    
    def test_admin_can_access_own_data(self, client, admin_user, get_admin_token):
        """Test admin user can access their own data."""
        admin_token = get_admin_token
        
        response = client.get(
            f"/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        returned_user = response.json()
        assert returned_user["id"] == str(admin_user.id)
        assert returned_user["email"] == admin_user.email
        assert returned_user["role"] == "admin"

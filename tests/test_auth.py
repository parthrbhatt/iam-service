import pytest
from fastapi.testclient import TestClient

class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_user_registration_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        user_data = response.json()
        assert user_data["name"] == test_user_data["name"]
        assert user_data["email"] == test_user_data["email"]
        assert user_data["date_of_birth"] == test_user_data["date_of_birth"]
        assert user_data["job_title"] == test_user_data["job_title"]
        assert user_data["role"] == "user"
        assert "id" in user_data
        assert "password" not in user_data
    
    def test_user_registration_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email fails."""
        # Create first user
        response1 = client.post("/users", json=test_user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        response2 = client.post("/users", json=test_user_data)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]
    
    def test_user_registration_short_password(self, client, test_user_data):
        """Test registration with password less than 12 characters fails."""
        test_user_data["password"] = "Short123!"  # Only 9 characters
        
        response = client.post("/users", json=test_user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("at least 12 characters" in str(error) for error in error_detail)

    
    def test_user_registration_invalid_email(self, client, test_user_data):
        """Test registration with invalid email format fails."""
        test_user_data["email"] = "invalid-email"
        
        response = client.post("/users", json=test_user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("email" in str(error).lower() for error in error_detail)
    
    def test_user_registration_missing_required_fields(self, client):
        """Test registration with missing required fields fails."""
        incomplete_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        response = client.post("/users", json=incomplete_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("required" in str(error).lower() for error in error_detail)
    
    def test_user_registration_extra_fields_rejected(self, client, test_user_data):
        """Test registration with extra fields is rejected."""
        # Add extra fields that shouldn't be allowed
        user_data_with_extra = {
            **test_user_data,
            "role": "admin",  # Should not be allowed
            "is_active": True,  # Should not be allowed
            "created_at": "2024-01-01T00:00:00Z",  # Should not be allowed
            "malicious_field": "hack_attempt"  # Should not be allowed
        }
        
        response = client.post("/users", json=user_data_with_extra)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        # Should mention that extra fields are not allowed
        assert any("extra" in str(error).lower() for error in error_detail)


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, create_test_user, test_user_data):
        """Test successful login."""
        response = client.post("/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_in" in token_data
        assert token_data["expires_in"] > 0
    
    def test_login_invalid_credentials(self, client, create_test_user, test_user_data):
        """Test login with invalid credentials fails."""
        response = client.post("/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post("/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials fails."""
        response = client.post("/login", json={
            "email": "test@example.com"
            # Missing password
        })
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("required" in str(error).lower() for error in error_detail)

    def test_login_extra_fields_rejected(self, client, create_test_user, test_user_data):
        """Test login with extra fields is rejected."""
        login_data_with_extra = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "remember_me": True,  # Should not be allowed
            "device_id": "device123",  # Should not be allowed
            "malicious_field": "hack_attempt"  # Should not be allowed
        }
        
        response = client.post("/login", json=login_data_with_extra)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        # Should mention that extra fields are not allowed
        assert any("extra" in str(error).lower() for error in error_detail)


class TestStrongPasswordEnforcement:
    """Test password validation during registration."""
    
    def test_password_too_short(self, client):
        """Test password less than 12 characters fails with HTTP 422."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "Short123!"  # Only 9 characters
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        # Check that the error mentions minimum length requirement
        assert any("at least 12 characters" in str(error) for error in error_detail)
    
    def test_password_missing_uppercase(self, client):
        """Test password without uppercase letter fails."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "lowercase123!"  # No uppercase
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("upper, lower, digit, and symbol" in str(error) for error in error_detail)
    
    def test_password_missing_lowercase(self, client):
        """Test password without lowercase letter fails."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "UPPERCASE123!"  # No lowercase
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("upper, lower, digit, and symbol" in str(error) for error in error_detail)
    
    def test_password_missing_digit(self, client):
        """Test password without digit fails."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "NoDigitsHere!"  # No digits
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("upper, lower, digit, and symbol" in str(error) for error in error_detail)
    
    def test_password_special_character_missing(self, client):
        """Test password without symbol fails."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "NoSymbols123"  # No special character
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
        
        error_detail = response.json()["detail"]
        assert any("upper, lower, digit, and symbol" in str(error) for error in error_detail)
    
    def test_password_valid(self, client):
        """Test valid password passes validation."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "job_title": "Developer",
            "password": "ValidPassword123!"  # Meets all requirements
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
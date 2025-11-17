"""
Tests for user endpoints.
"""
import pytest
from fastapi import status


class TestUserProfile:
    """User profile tests."""
    
    def test_get_profile_success(self, client):
        """Test retrieving profile of a logged-in user."""
        # Register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # Log in
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Retrieve profile
        response = client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "created_at" in data
    
    def test_get_profile_unauthorized(self, client):
        """Test retrieving profile without a token."""
        response = client.get("/api/user/profile")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_profile_invalid_token(self, client):
        """Test retrieving profile with an invalid token."""
        response = client.get(
            "/api/user/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserUpdate:
    """User profile update tests."""
    
    def test_update_email(self, client):
        """Test updating email."""
        # Registration and login
        client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Update email
        response = client.put(
            "/api/user/update",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "newemail@example.com"
    
    def test_update_password(self, client):
        """Test updating password."""
        # Registration and login
        client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "oldpassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "oldpassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Update password
        response = client.put(
            "/api/user/update",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "newpassword123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check if login with new password works
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "newpassword123"}
        )
        assert login_response.status_code == status.HTTP_200_OK

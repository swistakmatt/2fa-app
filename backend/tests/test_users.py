"""
Tests for user endpoints.
"""
import pytest
from fastapi import status


class TestUserProfile:
    """User profile tests."""
    
    def test_get_profile_success(self, client, active_user):
        """Test retrieving profile of a logged-in user."""
        response = client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {active_user['token']}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == active_user["email"]
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
    
    def test_update_email(self, client, active_user):
        """Test updating email."""
        response = client.put(
            "/api/user/update",
            headers={"Authorization": f"Bearer {active_user['token']}"},
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "newemail@example.com"
    
    def test_update_password(self, client, active_user):
        """Test updating password."""
        response = client.put(
            "/api/user/update",
            headers={"Authorization": f"Bearer {active_user['token']}"},
            json={"password": "newpassword123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify new password works
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": active_user["email"],
                "password": "newpassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_update_unauthorized(self, client):
        """Test updating profile without a token."""
        response = client.put(
            "/api/user/update",
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

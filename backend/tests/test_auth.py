"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestRegistration:
    """User registration tests."""
    
    def test_register_success(self, client):
        """Test successful registration of a new user."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["message"] == "User successfully registered"
    
    def test_register_duplicate_email(self, client):
        """Test registration with already existing email."""
        # First, register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # Attempt to register again with the same email
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "anotherpassword"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Test registration with password that is too short."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """User login tests."""
    
    def test_login_success(self, client):
        """Test successful login."""
        # First, register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # Log in
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert "user_id" in data
    
    def test_login_wrong_password(self, client):
        """Test login with incorrect password."""
        # Register a user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # Attempt to login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login of a non-existent user."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]


class TestLogout:
    """Logout tests."""
    
    def test_logout(self, client):
        """Test logout."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert "logged out" in response.json()["message"]

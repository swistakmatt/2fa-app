"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestRegistration:
    """User registration tests."""
    
    def test_register_success(self, client, db_session):
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
        # New flow: message indicates activation needed
        assert "activate" in data["message"].lower() or "check" in data["message"].lower()
    
    def test_register_creates_inactive_user(self, client, db_session):
        """Test that registration creates user with is_active=False."""
        from app.models.user import User
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        user = db_session.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.is_active == False
        assert user.backup_generated == False
    
    def test_register_sends_activation_email(self, client):
        """Test that registration sends activation email."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "emailtest@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        # Verify email mock was called
        client.mock_activation_email.assert_called_once()
    
    def test_register_duplicate_email(self, client):
        """Test registration with already existing email."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "anotherpassword123"
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
    
    def test_login_active_user_success(self, client, active_user):
        """Test successful login for active user."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": active_user["email"],
                "password": active_user["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == active_user["email"]
        assert "user_id" in data
    
    def test_login_inactive_user_fails(self, client, inactive_user):
        """Test that inactive user cannot login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": inactive_user["email"],
                "password": inactive_user["password"]
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not_activated" in response.json()["detail"]
    
    def test_login_wrong_password(self, client, active_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": active_user["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
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
    
    def test_login_generates_backup_codes_first_time(self, client, db_session):
        """Test that first login generates backup codes."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create active user without backup codes
        user = User(
            email="firstlogin@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            backup_generated=False
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "firstlogin@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "backup_codes" in data
        assert len(data["backup_codes"]) > 0
    
    def test_login_no_backup_codes_second_time(self, client, db_session):
        """Test that subsequent logins don't generate new backup codes."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create active user WITH backup_generated=True
        user = User(
            email="secondlogin@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            backup_generated=True
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "secondlogin@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "backup_codes" in data
        assert len(data["backup_codes"]) == 0  # Empty list

"""
Unit tests for password reset functionality.
"""
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.password_reset import (
    generate_reset_token,
    send_reset_email,
    reset_user_password
)
from app.core.config import settings
from app.models.user import User
from app.core.security import verify_password


class TestGenerateResetToken:
    """Tests for password reset token generation."""
    
    def test_generate_reset_token_contains_user_id(self):
        """Token contains user_id."""
        user_id = 123
        token = generate_reset_token(user_id)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["user_id"] == user_id
    
    def test_generate_reset_token_has_reset_type(self):
        """Token has type 'reset'."""
        token = generate_reset_token(user_id=1)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["type"] == "reset"
    
    def test_generate_reset_token_has_expiration(self):
        """Token has expiration date (15 minutes)."""
        token = generate_reset_token(user_id=1)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert "exp" in decoded


class TestSendResetEmail:
    """Tests for sending password reset email."""
    
    @pytest.mark.asyncio
    async def test_send_reset_email_existing_user(self, db_session):
        """Send email for existing user."""
        # Create user
        user = User(
            email="reset@example.com",
            hashed_password="hashed",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        with patch('app.services.password_reset.fm.send_message', new_callable=AsyncMock) as mock_send:
            await send_reset_email("reset@example.com", db_session)
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_reset_email_nonexistent_user(self, db_session):
        """For non-existent user, email is not sent (silent failure)."""
        with patch('app.services.password_reset.fm.send_message', new_callable=AsyncMock) as mock_send:
            await send_reset_email("nonexistent@example.com", db_session)
            mock_send.assert_not_called()


class TestResetUserPassword:
    """Tests for resetting user password."""
    
    def test_reset_user_password_success(self, db_session):
        """Successful password reset with valid token."""
        # Create user
        user = User(
            email="password@example.com",
            hashed_password="old_hash",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Generate token
        token = generate_reset_token(user.id)
        new_password = "NewSecurePassword123!"
        
        # Reset password
        reset_user_password(token, new_password, db_session)
        
        # Refresh user
        db_session.refresh(user)
        
        # Check if password was changed
        assert user.hashed_password != "old_hash"
        assert verify_password(new_password, user.hashed_password)
    
    def test_reset_user_password_invalid_token(self, db_session):
        """Invalid token."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            reset_user_password("invalid_token", "NewPassword123!", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Invalid or expired token" in exc_info.value.detail
    
    def test_reset_user_password_expired_token(self, db_session):
        """Expired token (after 15 minutes)."""
        from fastapi import HTTPException
        
        # Create user
        user = User(
            email="expired@example.com",
            hashed_password="old_hash",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Generate expired token (manually)
        expired_payload = {
            "user_id": user.id,
            "type": "reset",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired one minute ago
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            reset_user_password(expired_token, "NewPassword123!", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Invalid or expired token" in exc_info.value.detail
    
    def test_reset_user_password_wrong_token_type(self, db_session):
        """Token with wrong type."""
        from fastapi import HTTPException
        
        # Generate token with different type
        wrong_type_payload = {
            "user_id": 1,
            "type": "activation",  # Wrong type
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        wrong_token = jwt.encode(wrong_type_payload, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            reset_user_password(wrong_token, "NewPassword123!", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Invalid token type" in exc_info.value.detail
    
    def test_reset_user_password_user_not_found(self, db_session):
        """Token for non-existent user."""
        from fastapi import HTTPException
        
        # Generate token for non-existent user
        token = generate_reset_token(user_id=99999)
        
        with pytest.raises(HTTPException) as exc_info:
            reset_user_password(token, "NewPassword123!", db_session)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail


class TestPasswordResetEndpoints:
    """Tests for password reset endpoints."""
    
    def test_reset_request_success(self, client, db_session):
        """Password reset request for existing user."""
        # Create user
        user = User(
            email="endpoint@example.com",
            hashed_password="hashed",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/auth/password/reset-request",
            json={"email": "endpoint@example.com"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
    
    def test_reset_request_nonexistent_user(self, client):
        """Reset request for non-existent user (returns success for security)."""
        response = client.post(
            "/api/auth/password/reset-request",
            json={"email": "nonexistent@example.com"}
        )
        
        # For security reasons, endpoint doesn't reveal if user exists
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
    
    def test_reset_request_missing_email(self, client):
        """Missing email in request."""
        response = client.post(
            "/api/auth/password/reset-request",
            json={}
        )
        
        assert response.status_code == 400
        assert "Missing email" in response.json()["detail"]
    
    def test_reset_password_success(self, client, db_session):
        """Successful password reset through endpoint."""
        # Create user
        user = User(
            email="reset_endpoint@example.com",
            hashed_password="old_hash",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Generujemy token
        token = generate_reset_token(user.id)
        
        response = client.post(
            "/api/auth/password/reset",
            json={
                "token": token,
                "new_password": "NewSecurePassword123!"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "password_changed"
    
    def test_reset_password_missing_fields(self, client):
        """Missing required fields."""
        response = client.post(
            "/api/auth/password/reset",
            json={"token": "some_token"}  # Missing new_password
        )
        
        assert response.status_code == 400
        assert "Missing fields" in response.json()["detail"]
    
    def test_reset_password_invalid_token(self, client):
        """Invalid token."""
        response = client.post(
            "/api/auth/password/reset",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired token" in response.json()["detail"]

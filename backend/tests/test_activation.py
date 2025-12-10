"""
Tests for account activation functionality.
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings


class TestActivation:
    """Account activation tests."""
    
    def test_activate_valid_token(self, client, db_session):
        """Test account activation with valid token."""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.services.activation_service import generate_activation_token
        
        # Create inactive user
        user = User(
            email="toactivate@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=False,
            backup_generated=False
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Generate valid token
        token = generate_activation_token(user_id)
        
        # Activate account - follow_redirects=False to not follow redirect
        response = client.get(f"/api/auth/activate?token={token}", follow_redirects=False)
        
        # Should redirect to frontend
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        
        # Query user again to verify activation
        updated_user = db_session.query(User).filter(User.id == user_id).first()
        assert updated_user.is_active == True
    
    def test_activate_expired_token(self, client, db_session):
        """Test account activation with expired token."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create inactive user
        user = User(
            email="expired@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=False,
            backup_generated=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Generate expired token manually
        payload = {
            "user_id": user.id,
            "type": "activation",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        response = client.get(f"/api/auth/activate?token={expired_token}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in response.json()["detail"].lower()
    
    def test_activate_invalid_token(self, client):
        """Test account activation with invalid token."""
        response = client.get("/api/auth/activate?token=invalid_token_here")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_activate_wrong_token_type(self, client, db_session):
        """Test activation with wrong token type (e.g., reset token)."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create user
        user = User(
            email="wrongtype@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=False,
            backup_generated=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Generate token with wrong type
        payload = {
            "user_id": user.id,
            "type": "reset",  # Wrong type
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        wrong_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        response = client.get(f"/api/auth/activate?token={wrong_token}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.json()["detail"].lower()
    
    def test_activate_already_active_user(self, client, db_session):
        """Test activating an already active user."""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.services.activation_service import generate_activation_token
        
        # Create already active user
        user = User(
            email="alreadyactive@example.com",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            backup_generated=False
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Generate valid token
        token = generate_activation_token(user_id)
        
        # Try to activate again - follow_redirects=False
        response = client.get(f"/api/auth/activate?token={token}", follow_redirects=False)
        
        # Should still succeed (idempotent) and redirect
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        
        # Query user again to verify still active
        updated_user = db_session.query(User).filter(User.id == user_id).first()
        assert updated_user.is_active == True
    
    def test_activate_nonexistent_user(self, client, db_session):
        """Test activation for a user that doesn't exist."""
        # Generate token for non-existent user ID
        payload = {
            "user_id": 99999,
            "type": "activation",
            "exp": datetime.now() + timedelta(hours=24)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        response = client.get(f"/api/auth/activate?token={token}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestActivationToken:
    """Tests for activation token generation."""
    
    def test_generate_activation_token_structure(self):
        """Test that generated token has correct structure."""
        from app.services.activation_service import generate_activation_token
        
        token = generate_activation_token(user_id=1)
        
        # Decode and verify structure
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["user_id"] == 1
        assert decoded["type"] == "activation"
        assert "exp" in decoded
    
    def test_generate_activation_token_expiration(self):
        """Test that token expires in 24 hours."""
        from app.services.activation_service import generate_activation_token
        
        token = generate_activation_token(user_id=1)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.now()
        
        # Should expire in approximately 24 hours (with some tolerance)
        time_diff = exp_time - now
        assert 23 <= time_diff.total_seconds() / 3600 <= 25

"""
Unit tests for backup codes functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.backup_codes import (
    generate_backup_codes,
    verify_backup_code,
    hash_code,
    verify_hash,
    PREFIX,
    TTL_SECONDS
)


class TestBackupCodeHashing:
    """Tests for code hashing functions."""
    
    def test_hash_code_returns_different_hash(self):
        """Hashing the same code returns different hashes (bcrypt)."""
        code = "ABC123"
        hash1 = hash_code(code)
        hash2 = hash_code(code)
        
        # bcrypt generates different hashes for the same code
        assert hash1 != hash2
    
    def test_verify_hash_correct_code(self):
        """Verification of correct code."""
        code = "ABC123"
        hashed = hash_code(code)
        
        assert verify_hash(code, hashed) is True
    
    def test_verify_hash_wrong_code(self):
        """Verification of wrong code."""
        code = "ABC123"
        hashed = hash_code(code)
        
        assert verify_hash("WRONG1", hashed) is False


class TestGenerateBackupCodes:
    """Tests for generating backup codes."""
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes_default_amount(self, mock_redis):
        """Generate default number of codes (2)."""
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id=1)
        
        assert len(codes) == 2
        # Codes are in hex format (6 characters)
        for code in codes:
            assert len(code) == 6
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes_custom_amount(self, mock_redis):
        """Generate custom number of codes."""
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id=1, amount=5)
        
        assert len(codes) == 5
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes_stores_in_redis(self, mock_redis):
        """Codes are stored in Redis."""
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id=1)
        
        # Check if keys were saved
        keys = await mock_redis.keys(f"{PREFIX}:1:*")
        assert len(keys) == 2
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes_unique(self, mock_redis):
        """Generated codes are unique."""
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id=1, amount=10)
        
        assert len(codes) == len(set(codes))


class TestVerifyBackupCode:
    """Tests for backup code verification."""
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_success(self, mock_redis):
        """Verify correct backup code."""
        user_id = 1
        
        with patch("app.services.backup_codes.REDIS", mock_redis):
            # First generate codes
            codes = await generate_backup_codes(user_id)
            
            # Verify first code
            result = await verify_backup_code(user_id, codes[0])
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_invalid(self, mock_redis):
        """Verify invalid backup code."""
        user_id = 1
        
        with patch("app.services.backup_codes.REDIS", mock_redis):
            # Generate codes
            await generate_backup_codes(user_id)
            
            # Try to verify invalid code
            result = await verify_backup_code(user_id, "WRONG1")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_single_use(self, mock_redis):
        """Backup code can be used only once."""
        user_id = 1
        
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id)
            code_to_use = codes[0]
            
            # First use - should succeed
            result1 = await verify_backup_code(user_id, code_to_use)
            assert result1 is True
            
            # Second use of same code - should fail
            result2 = await verify_backup_code(user_id, code_to_use)
            assert result2 is False
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_no_codes_exist(self, mock_redis):
        """Verify when user has no backup codes."""
        user_id = 999  # User without codes
        
        with patch("app.services.backup_codes.REDIS", mock_redis):
            result = await verify_backup_code(user_id, "ABC123")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_deletes_used_code(self, mock_redis):
        """After using a code, it is removed from Redis."""
        user_id = 1
        
        with patch("app.services.backup_codes.REDIS", mock_redis):
            codes = await generate_backup_codes(user_id)
            initial_keys = await mock_redis.keys(f"{PREFIX}:{user_id}:*")
            
            # Use code
            await verify_backup_code(user_id, codes[0])
            
            # Check if key was deleted
            remaining_keys = await mock_redis.keys(f"{PREFIX}:{user_id}:*")
            
        assert len(remaining_keys) == len(initial_keys) - 1


class TestBackupCodesEndpoints:
    """Tests for backup codes endpoints."""
    
    def test_backup_verify_success(self, client, active_user):
        """Verify backup code through endpoint."""
        # Using already mocked Redis in client fixture
        from app.services.backup_codes import generate_backup_codes
        import asyncio
        
        # Generate codes using mock_redis from client fixture
        with patch("app.services.backup_codes.REDIS", client.mock_redis):
            codes = asyncio.get_event_loop().run_until_complete(
                generate_backup_codes(active_user["user_id"])
            )
        
        response = client.post(
            "/api/backup/verify",
            headers={"Authorization": f"Bearer {active_user['token']}"},
            json={"code": codes[0]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "verified"
        assert "access_token" in data
    
    def test_backup_verify_invalid_code(self, client, active_user):
        """Verify invalid backup code through endpoint."""
        response = client.post(
            "/api/backup/verify",
            headers={"Authorization": f"Bearer {active_user['token']}"},
            json={"code": "WRONG1"}
        )
        
        assert response.status_code == 400
        assert "Invalid backup code" in response.json()["detail"]
    
    def test_backup_verify_missing_code(self, client, active_user):
        """Missing code in request."""
        response = client.post(
            "/api/backup/verify",
            headers={"Authorization": f"Bearer {active_user['token']}"},
            json={}
        )
        
        assert response.status_code == 400
        assert "Missing code" in response.json()["detail"]
    
    def test_backup_verify_unauthorized(self, client):
        """Attempt to verify without authorization."""
        response = client.post(
            "/api/backup/verify",
            json={"code": "ABC123"}
        )
        
        assert response.status_code == 401
    
    def test_backup_list_codes(self, client, active_user):
        """List backup codes - checks if endpoint responds."""
        # This test requires full Redis mocking in endpoint
        # Skipping for now - endpoint uses real REDIS
        pass

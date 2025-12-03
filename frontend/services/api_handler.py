"""
API Handler for communication with FastAPI backend.
"""
import httpx
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api")


class APIHandler:
    """Handles all API communication with backend."""
    
    def __init__(self):
        self.base_url = BACKEND_API_URL
        self.timeout = 10.0
    
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with registration response
            
        Raises:
            httpx.HTTPStatusError: If registration fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user and trigger 2FA code sending.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with tmp_token for 2FA verification
            
        Raises:
            httpx.HTTPStatusError: If login fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
    
    async def verify_2fa(self, tmp_token: str, code: str) -> Dict[str, Any]:
        """
        Verify 2FA code and get JWT access token.
        
        Args:
            tmp_token: Temporary token from login
            code: 6-digit verification code
            
        Returns:
            Dict with access_token and token_type
            
        Raises:
            httpx.HTTPStatusError: If verification fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/verify-2fa",
                json={"tmp_token": tmp_token, "code": code}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile data.
        
        Args:
            access_token: JWT access token
            
        Returns:
            Dict with user profile data
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/user/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def update_profile(
        self, 
        access_token: str, 
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user profile.
        
        Args:
            access_token: JWT access token
            email: New email (optional)
            password: New password (optional)
            
        Returns:
            Dict with updated user data
            
        Raises:
            httpx.HTTPStatusError: If update fails
        """
        data = {}
        if email:
            data["email"] = email
        if password:
            data["password"] = password
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/user/update",
                headers={"Authorization": f"Bearer {access_token}"},
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Delete user account.
        
        Args:
            access_token: JWT access token
            
        Returns:
            Dict with deletion confirmation
            
        Raises:
            httpx.HTTPStatusError: If deletion fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/user/delete",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()


# Singleton instance
api_handler = APIHandler()

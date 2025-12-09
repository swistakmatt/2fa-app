"""
API Handler for communication with FastAPI backend.
"""
import httpx
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api")
BACKEND_GOOGLE_LOGIN_URL = os.getenv("BACKEND_GOOGLE_LOGIN_URL", "http://localhost:8000/api/auth/google/login")


class APIHandler:
    def __init__(self):
        self.base_url = BACKEND_API_URL
        self.timeout = 10.0

    # ---------------------------------------
    # AUTH
    # ---------------------------------------
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password}
            )
            r.raise_for_status()
            return r.json()

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            r.raise_for_status()
            return r.json()

    # ---------------------------------------
    # 2FA MAIN
    # ---------------------------------------
    async def send_code(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/2fa/send", headers=headers)
            r.raise_for_status()
            return r.json()

    async def verify_2fa(self, token: str, code: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/2fa/verify",
                params={"code": code},
                headers=headers
            )
            r.raise_for_status()
            return r.json()

    # ---------------------------------------
    # BACKUP CODES
    # ---------------------------------------
    async def verify_backup_code(self, token: str, code: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/2fa/backup/verify",
                json={"code": code},
                headers=headers
            )
            r.raise_for_status()
            return r.json()

    async def get_backup_count(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/2fa/backup/list", headers=headers)
            r.raise_for_status()
            return r.json()

    async def reset_backup_codes(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/2fa/backup/reset", headers=headers)
            r.raise_for_status()
            return r.json()

    # ---------------------------------------
    # PROFILE
    # ---------------------------------------
    async def get_profile(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(f"{self.base_url}/user/profile", headers=headers)
            r.raise_for_status()
            return r.json()

    async def update_profile(self, token: str, **data):
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.put(
                f"{self.base_url}/user/update",
                json=data,
                headers=headers
            )
            r.raise_for_status()
            return r.json()

    # ---------------------------------------
    # PASSWORD RESET
    # ---------------------------------------
    async def send_reset_link(self, email: str):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/auth/password/reset-request", json={"email": email})
            r.raise_for_status()
            return r.json()

    async def reset_password(self, token: str, new_password: str):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/auth/password/reset",
                json={"token": token, "new_password": new_password}
            )
            r.raise_for_status()
            return r.json()

    def get_google_login_url(self):
        return BACKEND_GOOGLE_LOGIN_URL


# Singleton instance
api_handler = APIHandler()

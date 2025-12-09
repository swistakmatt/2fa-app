import secrets
from app.redis_init import REDIS
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

PREFIX = "2fa:backup"
TTL_SECONDS = 60 * 60 * 24 * 30  

def hash_code(code: str) -> str:
    return pwd.hash(code)


def verify_hash(code: str, hashed: str) -> bool:
    return pwd.verify(code, hashed)

async def generate_backup_codes(user_id: int, amount: int = 2) -> list[str]:
    codes = []

    for _ in range(amount):
        plain = secrets.token_hex(3).upper()

        hashed = hash_code(plain)

        key = f"{PREFIX}:{user_id}:{hashed}"

        await REDIS.set(key, "1", ex=TTL_SECONDS)

        codes.append(plain)

    return codes


async def verify_backup_code(user_id: int, code: str) -> bool:
    pattern = f"{PREFIX}:{user_id}:*"
    keys = await REDIS.keys(pattern)

    for key in keys:
        stored_hash = key.split(":")[-1]

        if verify_hash(code, stored_hash):
            await REDIS.delete(key)
            return True

    return False

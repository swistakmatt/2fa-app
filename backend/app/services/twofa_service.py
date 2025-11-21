# app/services/twofa_service.py
import json
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Request
from jose import jwt
import redis.asyncio as redis_async

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User

# Redis client
REDIS = redis_async.from_url(str(settings.REDIS_URL), decode_responses=True)

def _code_key(user_id: int) -> str:
    return f"2fa:code:{user_id}"

def _attempt_key(user_id: int) -> str:
    return f"2fa:attempts:{user_id}"

def _block_user_key(user_id: int) -> str:
    return f"2fa:block:user:{user_id}"

def _block_ip_key(ip: str) -> str:
    return f"2fa:block:ip:{ip}"

def _generate_code() -> str:
    return str(secrets.randbelow(1_000_000)).zfill(6)

async def _is_blocked(user_id: int, ip: str):
    user_block = await REDIS.get(_block_user_key(user_id))
    ip_block = await REDIS.get(_block_ip_key(ip))
    return user_block or ip_block

async def _increase_block(user_id: int, ip: str):
    """Progressive block time: 30m → 1h → 8h → 24h."""
    times = [30, 60, 480, 1440]  # in minutes

    current = await REDIS.get(_block_user_key(user_id))
    level = int(current) if current else 0
    level = min(level, len(times) - 1)

    block_minutes = times[level]

    await REDIS.set(_block_user_key(user_id), level + 1, ex=block_minutes * 60)
    await REDIS.set(_block_ip_key(ip), level + 1, ex=block_minutes * 60)

async def send_2fa_code_via_email(user: User):
    existing = await REDIS.get(_code_key(user.id))

    now = datetime.utcnow()

    if existing:
        payload = json.loads(existing)
        last_sent = datetime.fromisoformat(payload["last_sent"])
        if (now - last_sent).total_seconds() < settings.TWO_FA_RESEND_SECONDS:
            raise HTTPException(
                status_code=429,
                detail="Please wait before requesting another code."
            )

    code = _generate_code()
    entry = {
        "code": code,
        "last_sent": now.isoformat()
    }

    await REDIS.set(
        _code_key(user.id),
        json.dumps(entry),
        ex=settings.TWO_FA_CODE_TTL_SECONDS
    )

    # SEND EMAIL
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=bool(settings.MAIL_USERNAME)
    )

    fm = FastMail(conf)
    msg = MessageSchema(
        subject="Your verification code",
        recipients=[user.email],
        body=f"Your code is: {code}",
        subtype="plain"
    )
    await fm.send_message(msg)

    return True

def generate_tmp_token(user_id: int):
    payload = {
        "user_id": user_id,
        "type": "tmp_token",
        "exp": datetime.utcnow() + timedelta(minutes=settings.TMP_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

async def verify_code(user_id: int, code: str, ip: str):
    # Check block
    if await _is_blocked(user_id, ip):
        raise HTTPException(status_code=403, detail="Too many attempts. Account temporarily blocked.")

    stored = await REDIS.get(_code_key(user_id))
    if not stored:
        raise HTTPException(status_code=400, detail="Code expired or not found.")

    stored_code = json.loads(stored)["code"]

    if stored_code != code:
        attempts = await REDIS.incr(_attempt_key(user_id))
        await REDIS.expire(_attempt_key(user_id), settings.TWO_FA_CODE_TTL_SECONDS)

        if attempts >= settings.TWO_FA_MAX_ATTEMPTS:
            await _increase_block(user_id, ip)

        raise HTTPException(status_code=400, detail="Invalid code.")

    # SUCCESS — reset attempts
    await REDIS.delete(_attempt_key(user_id))
    await REDIS.delete(_code_key(user_id))
    return True

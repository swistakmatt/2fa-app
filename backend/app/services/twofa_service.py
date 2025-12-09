import json
import secrets
from datetime import datetime

from fastapi import HTTPException
import redis.asyncio as redis_async

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.config import settings
from app.models.user import User

REDIS = redis_async.from_url(str(settings.REDIS_URL), decode_responses=True)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)

fm = FastMail(conf)


async def send_email(subject: str, recipients: list[str], body: str):
    msg = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="plain"
    )
    await fm.send_message(msg)


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
    return await REDIS.get(_block_user_key(user_id)) or await REDIS.get(_block_ip_key(ip))


async def _increase_block(user_id: int, ip: str):
    times = [30, 60, 480, 1440]
    current = await REDIS.get(_block_user_key(user_id))
    level = int(current) if current else 0
    level = min(level, len(times) - 1)
    duration = times[level] * 60

    await REDIS.set(_block_user_key(user_id), level + 1, ex=duration)
    await REDIS.set(_block_ip_key(ip), level + 1, ex=duration)


async def send_2fa_code_via_email(user: User):
    await REDIS.delete(_code_key(user.id))

    existing = await REDIS.get(_code_key(user.id))
    now = datetime.utcnow()

    if existing:
        payload = json.loads(existing)
        last_sent = datetime.fromisoformat(payload["last_sent"])
        if (now - last_sent).total_seconds() < settings.TWO_FA_RESEND_SECONDS:
            raise HTTPException(status_code=429, detail="Please wait before requesting another code.")

    code = _generate_code()
    entry = {"code": code, "last_sent": now.isoformat()}

    await REDIS.set(
        _code_key(user.id),
        json.dumps(entry),
        ex=settings.TWO_FA_CODE_TTL_SECONDS
    )

    await send_email(
        subject="Your verification code",
        recipients=[user.email],
        body=f"Your code is: {code}"
    )

    return True

async def verify_code(user_id: int, code: str, ip: str):
    if await _is_blocked(user_id, ip):
        raise HTTPException(403, "Too many attempts. Account temporarily blocked.")

    stored = await REDIS.get(_code_key(user_id))
    if not stored:
        raise HTTPException(400, "Code expired or not found.")

    real_code = json.loads(stored)["code"]

    if real_code != code:
        attempts = await REDIS.incr(_attempt_key(user_id))
        await REDIS.expire(_attempt_key(user_id), settings.TWO_FA_CODE_TTL_SECONDS)

        if attempts >= settings.TWO_FA_MAX_ATTEMPTS:
            await _increase_block(user_id, ip)

        raise HTTPException(400, "Invalid code.")

    await REDIS.delete(_attempt_key(user_id))
    await REDIS.delete(_code_key(user_id))

    return True

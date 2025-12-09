import jwt
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import HTTPException

from app.core.config import settings
from app.models.user import User
from sqlalchemy.orm import Session


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


def generate_activation_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "type": "activation",
        "exp": datetime.now() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def send_activation_email(email: str, token: str):
    link = f"{settings.PUBLIC_BACKEND_URL}/api/auth/activate?token={token}"

    body = f"Kliknij aby aktywować konto:\n\n{link}"

    msg = MessageSchema(
        subject="Aktywacja konta",
        recipients=[email],
        body=body,
        subtype="plain"
    )

    await fm.send_message(msg)


def activate_user(token: str, db: Session):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if decoded.get("type") != "activation":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = decoded.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"status": "activated"}

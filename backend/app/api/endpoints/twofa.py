from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import timedelta
from sqlalchemy.orm import Session

from app.services.twofa_service import send_2fa_code_via_email, verify_code
from app.services.backup_codes import (
    PREFIX,
    REDIS,
    generate_backup_codes,
    verify_backup_code
)
from app.core.security import get_current_user, create_access_token
from app.core.config import settings
from app.core.database import get_db

router = APIRouter()

@router.post("/send")
async def send_code(request: Request, user=Depends(get_current_user)):
    await send_2fa_code_via_email(user)
    return {"status": "sent"}

@router.post("/verify")
async def verify(request: Request, code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ip = request.client.host

    await verify_code(user.id, code, ip)

    pattern = f"{PREFIX}:{user.id}:*"
    keys = await REDIS.keys(pattern)
    count = len(keys)

    REQUIRED = 2

    if count < REQUIRED:
        missing = REQUIRED - count
        backup_codes = await generate_backup_codes(user.id, amount=missing)

        user.backup_generated = True
        db.commit()
        db.refresh(user)
    else:
        backup_codes = []

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "status": "verified",
        "access_token": token,
        "token_type": "bearer",
        "backup_codes": backup_codes
    }


@router.post("/backup/generate")
async def generate_codes(user=Depends(get_current_user), db: Session = Depends(get_db)):
    codes = await generate_backup_codes(user.id)

    user.backup_generated = True
    db.commit()
    db.refresh(user)

    return {"backup_codes": codes}


@router.post("/backup/reset")
async def reset_codes(user=Depends(get_current_user), db: Session = Depends(get_db)):
    pattern = f"{PREFIX}:{user.id}:*"
    keys = await REDIS.keys(pattern)

    for key in keys:
        await REDIS.delete(key)

    codes = await generate_backup_codes(user.id)

    user.backup_generated = True
    db.commit()
    db.refresh(user)

    return {"backup_codes": codes}


@router.post("/backup/verify")
async def verify_backup(payload: dict, user=Depends(get_current_user)):
    code = payload.get("code")

    if not code:
        raise HTTPException(400, "Missing code")

    ok = await verify_backup_code(user.id, code)

    if not ok:
        raise HTTPException(400, "Invalid backup code")

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "status": "verified",
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/backup/list")
async def list_codes(user=Depends(get_current_user)):
    pattern = f"{PREFIX}:{user.id}:*"
    keys = await REDIS.keys(pattern)

    return {"available": len(keys)}

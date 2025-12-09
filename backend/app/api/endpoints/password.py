from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.password_reset import send_reset_email, reset_user_password

router = APIRouter()

@router.post("/password/reset-request")
async def reset_request(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")

    await send_reset_email(email, db)

    return {"status": "sent"}


@router.post("/password/reset")
def reset_password(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("token")
    new_password = payload.get("new_password")

    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Missing fields")

    reset_user_password(token, new_password, db)
    return {"status": "password_changed"}

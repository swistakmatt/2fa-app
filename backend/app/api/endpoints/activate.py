from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/activate")
def activate_account(
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Activation token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid activation token")

    if decoded.get("type") != "activation":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = decoded.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        user.is_active = True
        db.commit()

    return RedirectResponse(url=f"{settings.FRONTEND_URL}?page=login&activated=1")

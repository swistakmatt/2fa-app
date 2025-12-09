from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import urllib.parse
import httpx
from fastapi.responses import RedirectResponse

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import RegisterResponse, LoginRequest
from app.services.activation_service import generate_activation_token, send_activation_email
from app.services.backup_codes import generate_backup_codes

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=False,
        backup_generated=False, 
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = generate_activation_token(new_user.id)
    await send_activation_email(new_user.email, token)

    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        message="Account created. Check your email to activate.",
    )


@router.post("/login")
async def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="not_activated")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    backup_codes = []
    if not user.backup_generated:
        backup_codes = await generate_backup_codes(user.id)
        user.backup_generated = True
        db.commit()

    return {
        "user_id": user.id,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
        "backup_codes": backup_codes,
    }


@router.get("/google/login")
async def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": settings.GOOGLE_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }

    url = settings.GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(settings.GOOGLE_TOKEN_URL, data=data)
        token_res.raise_for_status()
        tokens = token_res.json()

    google_access_token = tokens["access_token"]

    headers = {"Authorization": f"Bearer {google_access_token}"}

    async with httpx.AsyncClient() as client:
        userinfo_res = await client.get(settings.GOOGLE_USERINFO_URL, headers=headers)
        userinfo_res.raise_for_status()
        userinfo = userinfo_res.json()

    email = userinfo["email"]

    user = db.query(User).filter(User.email == email).first()

    if not user:
        import secrets
        random_password = secrets.token_urlsafe(32)

        user = User(
            email=email,
            hashed_password=get_password_hash(random_password),
            is_active=True,
            backup_generated=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token(data={"sub": email})
    frontend_url = f"{settings.FRONTEND_BASE_URL}?google_token={jwt_token}"
    return RedirectResponse(frontend_url)

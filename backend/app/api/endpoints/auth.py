"""
Authentication-related endpoints (registration, login).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import RegisterResponse, LoginResponse, ErrorResponse, LoginRequest, Verify2FARequest
from app.services.twofa_service import send_2fa_code_via_email, verify_code, generate_tmp_token
from jose import jwt, JWTError, ExpiredSignatureError

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        201: {"description": "User successfully registered"},
        400: {"model": ErrorResponse, "description": "Email already registered"},
    }
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user in the system.
    
    **Process:**
    1. Input data validation (email, password min. 8 characters)
    2. Check if user with this email already exists
    3. Hash password using bcrypt
    4. Create new user in database
    
    **Parameters:**
    - **email**: Unique user email address
    - **password**: Password (minimum 8 characters)
    
    **Returns:**
    - ID of newly created user
    - User email
    - Confirmation message
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        message="User successfully registered"
    )


# -----------------------------
# LOGIN (STEP 1 — send 2FA)
# -----------------------------
@router.post("/login")
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Send 2FA code
    await send_2fa_code_via_email(user)

    # Create tmp token
    tmp_token = generate_tmp_token(user.id)

    return {"detail": "2fa_required", "tmp_token": tmp_token}


# -----------------------------
# VERIFY 2FA (STEP 2 — get JWT)
# -----------------------------
@router.post("/verify-2fa")
async def verify_2fa(payload: Verify2FARequest, request: Request, db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(payload.tmp_token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="tmp_token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid tmp_token")

    user_id = decoded.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid tmp_token")

    ip = request.client.host

    await verify_code(user_id, payload.code, ip)

    # produce final JWT
    user = db.query(User).filter(User.id == user_id).first()

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, "token_type": "bearer"}


# -----------------------------
# LOGOUT
# -----------------------------
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    responses={
        200: {"description": "Successfully logged out"},
    }
)
async def logout():
    """
    Log user out.
    
    **Note:** With stateless JWT, logout is handled on the client side
    by removing the token. This endpoint mainly serves API consistency.
    
    In the future, a token blacklist or shortened validity period can be added.
    """
    return {"message": "Successfully logged out"}

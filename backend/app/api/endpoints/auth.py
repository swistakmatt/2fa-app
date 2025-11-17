"""
Authentication-related endpoints (registration, login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import RegisterResponse, LoginResponse, ErrorResponse

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


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    responses={
        200: {"description": "Successful login, JWT token returned"},
        401: {"model": ErrorResponse, "description": "Invalid email or password"},
    }
)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Log user into the system.
    
    **Process:**
    1. Input data validation
    2. Check if user exists in database
    3. Verify password (compare with bcrypt hash)
    4. Generate JWT token
    5. Return access token
    
    **Parameters:**
    - **email**: User email address
    - **password**: User password
    
    **Returns:**
    - **access_token**: JWT token for authorization
    - **token_type**: Token type (bearer)
    - **user_id**: Logged-in user ID
    - **email**: User email
    
    **Token usage:**
    ```
    Authorization: Bearer {access_token}
    ```
    """
    # Check if user exists
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )


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

"""
Security-related functions: password hashing, JWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Context for password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided password matches the hashed password.
    
    Args:
        plain_password: Password in plain text
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    # Bcrypt has a 72-byte limit - truncate password if longer
    password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes password using bcrypt.
    
    Args:
        password: Password in plain text
        
    Returns:
        str: Hashed password
        
    Note:
        Bcrypt has a 72-byte limit. Longer passwords are automatically truncated.
    """
    # Bcrypt has a 72-byte limit - truncate password if longer
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token.
    
    Args:
        data: Data to encode in token (e.g. {"sub": email})
        expires_delta: Optional token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodes JWT token and returns user email.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Optional[str]: User email or None if token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
            
        return email
    except JWTError:
        return None

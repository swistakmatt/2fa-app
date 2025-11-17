"""
User management-related endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.auth import ErrorResponse

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    responses={
        200: {"description": "User profile data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    }
)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves currently logged-in user's profile data.
    
    **Required authorization:** JWT token in Authorization header
    
    **Returns:**
    - **id**: User ID
    - **email**: Email address
    - **is_active**: Account activity status
    - **created_at**: Account creation date
    - **updated_at**: Last update date
    
    **Usage example:**
    ```
    GET /api/user/profile
    Authorization: Bearer {access_token}
    ```
    """
    return current_user


@router.put(
    "/update",
    response_model=UserResponse,
    summary="Update user data",
    responses={
        200: {"description": "User data has been updated"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Email already taken"},
    }
)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Updates user profile data.
    
    **Required authorization:** JWT token in Authorization header
    
    **Parameters (optional):**
    - **email**: New email address
    - **password**: New password (minimum 8 characters)
    
    **Returns:**
    - Updated user data
    
    **Notes:**
    - Can update email, password, or both simultaneously
    - If no parameters provided, current data is returned
    - New email must be unique in the system
    """
    # Check if there's any data to update
    if not user_update.email and not user_update.password:
        return current_user
    
    # Update email
    if user_update.email and user_update.email != current_user.email:
        # Check if new email is not already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        current_user.email = user_update.email
    
    # Update password
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
    responses={
        200: {"description": "Account has been deleted"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    }
)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deletes currently logged-in user's account.
    
    **Required authorization:** JWT token in Authorization header
    
    **Warning:** This operation is irreversible!
    
    **Alternative:** Account deactivation instead of deletion
    (setting is_active = False)
    """
    # Option 1: Complete user deletion
    db.delete(current_user)
    db.commit()
    
    # Option 2 (recommended): Account deactivation
    # current_user.is_active = False
    # db.commit()
    
    return {"message": "Account successfully deleted"}

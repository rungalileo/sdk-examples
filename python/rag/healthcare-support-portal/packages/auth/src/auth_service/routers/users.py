from common.auth import get_current_user, get_password_hash
from common.db import get_db
from common.models import User
from common.oso_sync import (
    sync_admin_global_access,
    sync_department_change,
    sync_user_role_change,
)
from common.schemas import UserCreate, UserResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    List users (admin only - bypassing OSO for user management)
    """
    # Check if current user is admin - manual check instead of OSO
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list users",
        )

    # Get all users without OSO filtering since we already validated admin role
    users = db.query(User).offset(skip).limit(limit).all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specific user (admin only or self)
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check authorization - admin can read any user, users can read themselves
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user",
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user (admin only)
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check authorization - only admin can update users
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update users",
        )

    # Track changes for OSO sync
    old_role = user.role
    old_department = user.department

    # Update user fields
    user.username = user_update.username
    user.email = user_update.email
    user.role = user_update.role
    user.department = user_update.department

    db.commit()
    db.refresh(user)

    # Sync OSO facts if role or department changed
    try:
        if old_role != user.role:
            sync_user_role_change(user, old_role)

        if old_department != user.department:
            sync_department_change(user, old_department)
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to sync OSO facts for user {user.id}: {e}")

    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new user (admin only)
    """
    # Check if current user has admin role (only admins can create users)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create new users",
        )

    # Check if user already exists
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        department=user_data.department,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Sync OSO facts for new user
    try:
        if new_user.role == "admin":
            sync_admin_global_access(new_user)
        print(f"Synced OSO facts for new user {new_user.username}")
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to sync OSO facts for new user {new_user.id}: {e}")

    return new_user

"""HER AI — Authentication API Endpoints.

Provides:
  - User registration with Argon2id password hashing.
  - User login (JSON & OAuth2 form compatible) with JWT issuance.
  - Current user verification (/api/auth/me).
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import AuthResponse, UserLogin, UserRegister
from app.schemas.profile import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Register a new user account with Argon2id hashed password and receive an initial JWT access token."""
    # Check if username or email is already taken
    existing_user = db.execute(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
    ).scalar_one_or_none()

    if existing_user:
        if existing_user.username == payload.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already registered.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already registered.",
        )

    # Hash password with Argon2id
    hashed = hash_password(payload.password)

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("New user registered successfully: %s (%s)", user.username, user.id)

    token = create_access_token(
        subject=str(user.id),
        claims={"username": user.username, "email": user.email},
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user,
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Authenticate with username/email and password to receive a JWT access token."""
    user = db.execute(
        select(User).where(
            or_(
                User.username == payload.username_or_email,
                User.email == payload.username_or_email,
            )
        )
    ).scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token = create_access_token(
        subject=str(user.id),
        claims={"username": user.username, "email": user.email},
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user,
    )


@router.post("/token", response_model=AuthResponse, include_in_schema=False)
def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> AuthResponse:
    """OAuth2 password request form endpoint for Swagger UI authorization dialog."""
    login_payload = UserLogin(
        username_or_email=form_data.username,
        password=form_data.password,
    )
    return login(login_payload, db)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve details of the currently authenticated user."""
    return current_user


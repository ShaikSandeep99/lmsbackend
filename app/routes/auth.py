# app/routes/auth.py
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RoleEnum, PasswordResetToken
from app.schemas import (
    UserCreate,
    LoginIn,
    TokenPair,
    UserOut,
    RefreshIn,
    ForgotIn,
    ResetIn,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,  # make sure this exists in security.py
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = (data.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # Unique email check
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        full_name=data.full_name,
        phone_number=data.phone_number,  # schema alias handles phoneNumber -> phone_number
        hashed_password=data.password,
        role=RoleEnum.student,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(form: LoginIn, db: Session = Depends(get_db)):
    # Normalize email to avoid case/space issues
    email = (form.email or "").strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # Fail fast if user not found or password invalid
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # sub should be user id; include role as a claim
    access_token  = create_access_token(sub=str(user.id), extra={"role": str(user.role)})
    refresh_token = create_refresh_token(sub=str(user.id))
    return TokenPair(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshIn):
    """
    Expects a refresh token; returns a fresh access/refresh pair.
    """
    try:
        payload = decode_refresh_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = payload["sub"]  # we store user id in sub
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return TokenPair(
        access_token=create_access_token(sub=user_id),
        refresh_token=create_refresh_token(sub=user_id),
    )


@router.post("/forgot")
def forgot(data: ForgotIn, db: Session = Depends(get_db)):
    """
    Creates a one-time password reset token row (dev flow: returns token).
    In production, email/SMS the token instead of returning it.
    """
    email = (data.email or "").strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user:
        reset_token = generate_reset_token(db, user)
        # TODO: send email with reset link containing the token
        return {"message": "Reset token generated (dev)", "token": reset_token}
    # Don’t leak user existence
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset")
def reset(data: ResetIn, db: Session = Depends(get_db)):
    prt = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == data.token)
        .first()
    )
    now = datetime.now(timezone.utc)

    if not prt or prt.used or prt.expires_at <= now:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.get(User, prt.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    user.hashed_password = hash_password(data.new_password)
    prt.used = True
    db.commit()
    return {"message": "Password reset successful"}


# --- helpers ---

def generate_reset_token(db: Session, user: User, lifetime_minutes: int = 30) -> str:
    """
    Insert a PasswordResetToken row and return the raw token string.
    """
    import secrets

    raw = secrets.token_urlsafe(32)
    record = PasswordResetToken(
        user_id=user.id,
        token=raw,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=lifetime_minutes),
        used=False,
    )
    db.add(record)
    db.commit()
    return raw

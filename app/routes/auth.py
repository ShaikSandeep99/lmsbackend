from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RoleEnum, PasswordResetToken
from app.schemas import UserCreate, LoginIn, TokenPair, RefreshIn, ForgotIn, ResetIn, UserOut
from app.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh
from app.utils import generate_reset_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, full_name=data.full_name,
phone_number=data.phone_number,
                hashed_password=hash_password(data.password),
                role=RoleEnum.student)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(form: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")
    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email)
    )

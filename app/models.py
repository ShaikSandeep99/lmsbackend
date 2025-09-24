from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class RoleEnum(str, PyEnum):
    admin = "admin"
    mentor = "mentor"
    student = "student"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.student, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    user = relationship("User", back_populates="reset_tokens")

class Student_data(Base):
    __tablename__ = "Student_Data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


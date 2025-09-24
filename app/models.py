# app/models.py
from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Integer, DateTime, Date, ForeignKey, Enum, Boolean, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# --- Enums ---

class RoleEnum(str, PyEnum):
    admin = "admin"
    mentor = "mentor"
    student = "student"


class GenderEnum(str, PyEnum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class ModeEnum(str, PyEnum):
    online = "online"
    offline = "offline"
    hybrid = "hybrid"


# --- Core auth user & reset token ---

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

    # One-to-one profiles (only one will exist depending on role)
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    mentor_profile: Mapped[Optional["MentorProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="reset_tokens")


# --- Student profile ---

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_student_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # requested fields
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(20))
    dob: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(Enum(GenderEnum))
    address: Mapped[Optional[str]] = mapped_column(Text)

    # uploads (store paths/URLs; real files handled by storage layer)
    photo_url: Mapped[Optional[str]] = mapped_column(String(512))
    resume_url: Mapped[Optional[str]] = mapped_column(String(512))

    # interests / referrals
    course_interest: Mapped[Optional[str]] = mapped_column(String(255))  # e.g., "Python Full Stack"
    is_referred: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="student_profile")


# --- Technology catalog & mentor link (many-to-many) ---

class Technology(Base):
    __tablename__ = "technologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # examples to seed: "Python", "Java", "Web Technologies", "React", "Django", "Spring Boot", etc.

    mentor_links: Mapped[List["MentorTechnology"]] = relationship(
        "MentorTechnology", back_populates="technology", cascade="all, delete-orphan"
    )


class MentorTechnology(Base):
    __tablename__ = "mentor_technologies"
    __table_args__ = (
        UniqueConstraint("mentor_profile_id", "technology_id", name="uq_mentor_tech"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mentor_profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mentor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    technology_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    mentor_profile: Mapped["MentorProfile"] = relationship("MentorProfile", back_populates="technologies_link")
    technology: Mapped["Technology"] = relationship("Technology", back_populates="mentor_links")


# --- Mentor profile ---

class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_mentor_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # requested + sensible extras for a good mentor profile
    name: Mapped[str] = mapped_column(String(150))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    dob: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(Enum(GenderEnum))
    address: Mapped[Optional[str]] = mapped_column(Text)

    # experience
    experience_summary: Mapped[Optional[str]] = mapped_column(Text)  # short bio / domains mentored
    total_experience_years: Mapped[Optional[int]] = mapped_column(Integer)  # whole years
    total_experience_months: Mapped[Optional[int]] = mapped_column(Integer)  # leftover months 0-11

    # uploads & links
    resume_url: Mapped[Optional[str]] = mapped_column(String(512))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(512))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(512))

    # preferences
    preferred_mode: Mapped[Optional[ModeEnum]] = mapped_column(Enum(ModeEnum))  # online/offline/hybrid
    availability_hours_per_week: Mapped[Optional[int]] = mapped_column(Integer)

    # many-to-many technologies
    technologies_link: Mapped[List["MentorTechnology"]] = relationship(
        "MentorTechnology", back_populates="mentor_profile", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="mentor_profile")

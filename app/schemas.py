# app/schemas.py
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ------------------------
# Helpers
# ------------------------
def _allow_local_email(v: str) -> str:
    v = (v or "").strip()
    if "@" not in v or v.startswith("@") or v.endswith("@"):
        raise ValueError("Invalid email format")
    # Accept dev/test domains (.local, .test, localhost, etc.)
    return v.lower()


# ------------------------
# Token schemas
# ------------------------
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ------------------------
# User schemas
# ------------------------
class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")

    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    whatsapp_number: Optional[str] = Field(default=None, alias="whatsappNumber")
    dob: Optional[str] = Field(default=None, alias="DOB")
    gender: Optional[str] = Field(default=None, alias="gender")
    address: Optional[str] = Field(default=None, alias="address")
    password: Optional[str] = Field(default=None, alias="password")
    confirm_password: Optional[str] = Field(default=None, alias="confirmPassword")
    upload_photo: Optional[str] = Field(default=None, alias="uploadPhoto")
    upload_resume: Optional[str] = Field(default=None, alias="uploadResume")
    course_interest: Optional[str] = Field(default=None, alias="courseInterest")
    is_referred: Optional[bool] = Field(default=False, alias="isReferred")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _allow_local_email(v)


class UserCreate(UserBase):
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    is_active: bool

    # v2: from_attributes replaces orm_mode
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ------------------------
# Auth input schemas
# ------------------------
class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _allow_local_email(v)


class RefreshIn(BaseModel):
    refresh_token: str


class ForgotIn(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _allow_local_email(v)


class ResetIn(BaseModel):
    token: str
    new_password: str


# ------------------------
# Admin schemas
# ------------------------
class MentorCreate(BaseModel):
    email: str
    full_name: Optional[str] = Field(default=None, alias="fullName")
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    password: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _allow_local_email(v)

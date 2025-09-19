from typing import Optional
from pydantic import BaseModel, EmailStr, Field


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
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[int] = Field(default=None, alias="phoneNumber") 

class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True   # ✅ replaces orm_mode in Pydantic v2


# ------------------------
# Auth input schemas
# ------------------------
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str
    new_password: str


# ------------------------
# Admin schemas
# ------------------------
class MentorCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_Number: Optional[int] = None
    password: str
class Config:
        populate_by_name = True
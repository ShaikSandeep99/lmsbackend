# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import require_role
from app.models import RoleEnum, User
from app.database import get_db
from app.schemas import MentorCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/create-mentor", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_mentor(data: MentorCreate, db: Session = Depends(get_db)):
    # Check duplicate
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    # Create mentor
    mentor = User(
        email=data.email,
        full_name=data.full_name,
        phone_number=data.phoneNumber,
        hashed_password=hash_password(data.password),
        role=RoleEnum.mentor,
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    return mentor

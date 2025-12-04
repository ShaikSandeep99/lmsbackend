
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import date

# from app.deps import require_role
# from app.models import RoleEnum, User, Batch
# from app.database import get_db
# from app.schemas import MentorCreate, UserOut, BatchCreate, BatchOut
# from app.security import hash_password

# router = APIRouter(prefix="/admin", tags=["admin"])

# # ----------------------
# # Create a mentor
# # ----------------------
# @router.post("/create-mentor", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
# def create_mentor(data: MentorCreate, db: Session = Depends(get_db)):
#     if db.query(User).filter(User.email == data.email).first():
#         raise HTTPException(status_code=400, detail="Email already exists")
#     mentor = User(
#         email=data.email,
#         full_name=data.full_name,
#         phone_number=data.phone_number,
#         hashed_password=hash_password(data.password),
#         role=RoleEnum.mentor,
#     )
#     db.add(mentor)
#     db.commit()
#     db.refresh(mentor)
#     return mentor

# # ----------------------
# # Create a new batch
# # ----------------------
# @router.post("/dashboard/batches/add_batch", response_model=BatchOut, dependencies=[Depends(require_role(RoleEnum.admin))])
# def create_batch(data: BatchCreate, db: Session = Depends(get_db)):
#     batch = Batch(**data.model_dump())
#     db.add(batch)
#     db.commit()
#     db.refresh(batch)
#     return batch

# # ----------------------
# # Get all batches
# # ----------------------
# @router.get("/dashboard/batches", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
# def get_all_batches(db: Session = Depends(get_db)):
#     return db.query(Batch).all()

# # ----------------------
# # Get batches by status
# # ----------------------
# @router.get("/dashboard/batches/completed", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
# def get_completed_batches(db: Session = Depends(get_db)):
#     today = date.today()
#     return db.query(Batch).filter(Batch.completion_date < today).all()

# @router.get("/dashboard/batches/ongoing", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
# def get_ongoing_batches(db: Session = Depends(get_db)):
#     today = date.today()
#     return db.query(Batch).filter(Batch.start_date <= today, Batch.completion_date >= today).all()

# @router.get("/dashboard/batches/upcoming", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
# def get_upcoming_batches(db: Session = Depends(get_db)):
#     today = date.today()
#     return db.query(Batch).filter(Batch.start_date > today).all()

# # ----------------------
# # Update a batch
# # ----------------------
# @router.put("/dashboard/batches/{batch_id}", response_model=BatchOut, dependencies=[Depends(require_role(RoleEnum.admin))])
# def update_batch(batch_id: int, data: BatchCreate, db: Session = Depends(get_db)):
#     batch = db.query(Batch).filter(Batch.id == batch_id).first()
#     if not batch:
#         raise HTTPException(status_code=404, detail="Batch not found")
#     for key, value in data.model_dump().items():
#         setattr(batch, key, value)
#     db.commit()
#     db.refresh(batch)
#     return batch

# # ----------------------
# # Delete a batch
# # ----------------------
# @router.delete("/dashboard/batches/{batch_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
# def delete_batch(batch_id: int, db: Session = Depends(get_db)):
#     batch = db.query(Batch).filter(Batch.id == batch_id).first()
#     if not batch:
#         raise HTTPException(status_code=404, detail="Batch not found")
#     db.delete(batch)
#     db.commit()
#     return {"detail": "Batch deleted successfully"}


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.deps import require_role
from app.models import RoleEnum, User, Batch, MentorProfile
from app.database import get_db
from app.schemas import MentorCreate, UserOut, BatchCreate, BatchOut
from app.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])

# ----------------------
# Create a mentor
# ----------------------
@router.post("/create-mentor", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_mentor(data: MentorCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user record
    mentor_user = User(
        email=data.email,
        full_name=data.full_name,
        phone_number=data.phone_number,
        hashed_password=hash_password(data.password),
        role=RoleEnum.mentor,
    )
    db.add(mentor_user)
    db.commit()
    db.refresh(mentor_user)

    # Create mentor profile linked to the user
    mentor_profile = MentorProfile(user_id=mentor_user.id)
    db.add(mentor_profile)
    db.commit()
    db.refresh(mentor_profile)

    return mentor_user


# ----------------------
# Create a new batch
# ----------------------
@router.post("/dashboard/batches/add_batch", response_model=BatchOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_batch(data: BatchCreate, db: Session = Depends(get_db)):
    # Check if mentor exists in mentor_profiles
    mentor_profile = db.query(MentorProfile).filter(MentorProfile.id == data.mentor_id).first()
    if not mentor_profile:
        raise HTTPException(status_code=400, detail="Invalid mentor_id: mentor does not exist")

    # Create batch
    batch = Batch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


# ----------------------
# Get all batches
# ----------------------
@router.get("/dashboard/batches", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def get_all_batches(db: Session = Depends(get_db)):
    return db.query(Batch).all()


# ----------------------
# Get batches by status
# ----------------------
@router.get("/dashboard/batches/completed", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def get_completed_batches(db: Session = Depends(get_db)):
    today = date.today()
    return db.query(Batch).filter(Batch.completion_date < today).all()

@router.get("/dashboard/batches/ongoing", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def get_ongoing_batches(db: Session = Depends(get_db)):
    today = date.today()
    return db.query(Batch).filter(Batch.start_date <= today, Batch.completion_date >= today).all()

@router.get("/dashboard/batches/upcoming", response_model=list[BatchOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def get_upcoming_batches(db: Session = Depends(get_db)):
    today = date.today()
    return db.query(Batch).filter(Batch.start_date > today).all()


# ----------------------
# Update a batch
# ----------------------
@router.put("/dashboard/batches/{batch_id}", response_model=BatchOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def update_batch(batch_id: int, data: BatchCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    for key, value in data.model_dump().items():
        setattr(batch, key, value)
    db.commit()
    db.refresh(batch)
    return batch


# ----------------------
# Delete a batch
# ----------------------
@router.delete("/dashboard/batches/{batch_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(batch)
    db.commit()
    return {"detail": "Batch deleted successfully"}

from app.config import settings
from app.database import SessionLocal, engine, Base
from app.models import User, RoleEnum
from app.security import hash_password

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
            admin = User(
                email=settings.ADMIN_EMAIL,
                full_name="System Admin",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role=RoleEnum.admin
            )
            db.add(admin)
            db.commit()
            print("Admin created:", settings.ADMIN_EMAIL)
        else:
            print("Admin already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

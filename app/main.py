from fastapi import FastAPI
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LMS API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"status": "ok"}

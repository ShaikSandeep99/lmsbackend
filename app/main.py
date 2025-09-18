from fastapi import FastAPI
from . import models, database
from .routes import user_routes

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FastAPI with Postgres & JWT")

app.include_router(user_routes.router)

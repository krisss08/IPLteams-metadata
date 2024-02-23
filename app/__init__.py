from fastapi import APIRouter

from app.api import models 

api_router = APIRouter()

api_router.include_router(models.router, prefix="/models", tags=["Models"])


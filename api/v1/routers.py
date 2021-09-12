from fastapi import APIRouter
from .endpoints import amazon, azure

router = APIRouter()
router.include_router(amazon.router, tags=["amazon"])
router.include_router(azure.router, tags=["azure"])

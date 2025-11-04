"""Central API router that includes all endpoint routers."""

from fastapi import APIRouter

from app.core.config import settings
from app.routers import health

# Create main API router
api_router = APIRouter()

# Include all routers here
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Add more routers as you create them:
# from app.routers import users, products, etc.
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(products.router, prefix="/products", tags=["Products"])

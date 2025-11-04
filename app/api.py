"""Central API router that includes all endpoint routers."""

from fastapi import APIRouter

from app.core.config import settings
from app.routers import health, users
from app.routers.public import auth as public_auth

# Create main API router
api_router = APIRouter()

# Public routers (no authentication required)
api_router.include_router(public_auth.router, prefix="/public", tags=["Public"])

# Health check routers (no authentication required)
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# User management routers (authentication required, mostly admin-only)
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Add more routers as you create them:
# from app.routers import users, products, etc.
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(products.router, prefix="/products", tags=["Products"])

"""Central API router that includes all endpoint routers."""

from fastapi import APIRouter

from app.core.config import settings
from app.routers import health
from app.routers.public import auth as public_auth
from app.routers import users
from app.routers import audit_logs


def create_api_router() -> APIRouter:
    """Create and configure the main API router."""
    router = APIRouter()
    
    # Public routes (no authentication required)
    router.include_router(public_auth.router, prefix="/public", tags=["Public"])
    
    # Health check
    router.include_router(health.router, prefix="/health", tags=["Health"])
    
    # Protected routes (authentication required)
    router.include_router(users.router, prefix="/users", tags=["Users"])
    router.include_router(audit_logs.router, prefix="/audit_logs", tags=["Audit Logs"])
    
    return router


# Create the API router instance
api_router = create_api_router()

# Add more routers as you create them:
# from app.routers import users, products, etc.
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(products.router, prefix="/products", tags=["Products"])

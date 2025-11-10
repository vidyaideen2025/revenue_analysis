"""Health check endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.response import APIResponse


router = APIRouter(tags=["Health"])


@router.get("/")
async def health_check() -> JSONResponse:
    """
    Basic health check endpoint.
    
    Returns:
        Standardized response with health status
    """
    data = {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy"
    }
    
    return APIResponse.success(
        message="Application is healthy",
        data=data
    )


@router.get("/db")
async def database_health_check(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> JSONResponse:
    """
    Database health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Standardized response with database status
    """
    try:
        # Execute a simple query to check database connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        data = {
            "database": "connected",
            "status": "healthy"
        }
        
        return APIResponse.success(
            message="Database connection is healthy",
            data=data
        )
    except Exception as e:
        data = {
            "database": "disconnected",
            "error": str(e)
        }
        
        return APIResponse.internal_error(
            message="Database connection failed",
            data=data
        )

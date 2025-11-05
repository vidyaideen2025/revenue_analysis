"""Public authentication endpoints (no authentication required)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import APIResponse
from app.services.auth import auth_service
from app.schemas.user import LoginRequest
from app.utils.audit import log_login


router = APIRouter(tags=["Public - Authentication"])


@router.post("/login", response_model=None)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> JSONResponse:
    """
    User login endpoint.
    
    **Public endpoint - No authentication required**
    
    Args:
        login_data: Login credentials (email and password)
        db: Database session
        
    Returns:
        JWT access token on successful authentication
        
    Example:
        ```json
        POST /api/v1/public/login
        Content-Type: application/json
        
        {
            "email": "admin@revenueguardian.com",
            "password": "Admin@123"
        }
        ```
    """
    user = await auth_service.authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )
    
    if not user:
        # Log failed login attempt
        await log_login(
            db=db,
            user_id=None,
            email=login_data.email,
            request=request,
            success=False
        )
        
        return APIResponse.unauthorized(
            message="Incorrect email or password",
            data={"detail": "Authentication failed"}
        )
    
    # Log successful login
    await log_login(
        db=db,
        user_id=user.id,
        email=user.email,
        request=request,
        success=True
    )
    
    # Create access token
    access_token = auth_service.create_user_token(user)
    
    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }
    
    return APIResponse.success(
        message="Login successful",
        data=token_data,
        status_code=status.HTTP_200_OK
    )

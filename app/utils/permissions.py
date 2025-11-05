"""Permission checking utilities for RBAC."""

from functools import wraps
from typing import Callable
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.permission import Permission, Role, role_permissions


class PermissionChecker:
    """Utility class for checking user permissions."""
    
    @staticmethod
    async def user_has_permission(
        db: AsyncSession,
        user: User,
        permission_code: str
    ) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            db: Database session
            user: User to check
            permission_code: Permission code (e.g., "reconciliation.file.upload")
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admin role (role=1) has all permissions
        if user.role == 1:
            return True
        
        # Get user's role permissions
        query = (
            select(Permission)
            .join(role_permissions)
            .join(Role)
            .where(
                Role.code == _get_role_code_from_value(user.role),
                Permission.code == permission_code,
                Permission.is_active == True,
                Role.is_active == True
            )
        )
        
        result = await db.execute(query)
        permission = result.scalar_one_or_none()
        
        return permission is not None
    
    @staticmethod
    async def user_has_any_permission(
        db: AsyncSession,
        user: User,
        permission_codes: list[str]
    ) -> bool:
        """
        Check if user has any of the specified permissions.
        
        Args:
            db: Database session
            user: User to check
            permission_codes: List of permission codes
            
        Returns:
            True if user has at least one permission
        """
        for code in permission_codes:
            if await PermissionChecker.user_has_permission(db, user, code):
                return True
        return False
    
    @staticmethod
    async def user_has_all_permissions(
        db: AsyncSession,
        user: User,
        permission_codes: list[str]
    ) -> bool:
        """
        Check if user has all of the specified permissions.
        
        Args:
            db: Database session
            user: User to check
            permission_codes: List of permission codes
            
        Returns:
            True if user has all permissions
        """
        for code in permission_codes:
            if not await PermissionChecker.user_has_permission(db, user, code):
                return False
        return True
    
    @staticmethod
    async def get_user_permissions(
        db: AsyncSession,
        user: User
    ) -> list[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            db: Database session
            user: User to get permissions for
            
        Returns:
            List of Permission objects
        """
        # Admin has all permissions
        if user.role == 1:
            query = select(Permission).where(Permission.is_active == True)
            result = await db.execute(query)
            return list(result.scalars().all())
        
        # Get role-based permissions
        query = (
            select(Permission)
            .join(role_permissions)
            .join(Role)
            .where(
                Role.code == _get_role_code_from_value(user.role),
                Permission.is_active == True,
                Role.is_active == True
            )
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())


def _get_role_code_from_value(role_value: int) -> str:
    """Convert role integer value to role code."""
    role_map = {
        1: "ADMIN",
        2: "OPERATIONS",
        3: "CXO"
    }
    return role_map.get(role_value, "OPERATIONS")


def require_permission(permission_code: str):
    """
    Decorator to require a specific permission for an endpoint.
    
    Usage:
        @router.post("/upload")
        @require_permission("reconciliation.file.upload")
        async def upload_file(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract db and current_user from kwargs
            db = kwargs.get('db')
            current_user = kwargs.get('current_user')
            
            if not db or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session or user not found in request context"
                )
            
            # Check permission
            has_permission = await PermissionChecker.user_has_permission(
                db, current_user, permission_code
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required permission: {permission_code}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permission_codes: str):
    """
    Decorator to require any of the specified permissions.
    
    Usage:
        @router.get("/dashboard")
        @require_any_permission("dashboard.executive.read", "dashboard.operations.read")
        async def view_dashboard(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db = kwargs.get('db')
            current_user = kwargs.get('current_user')
            
            if not db or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session or user not found in request context"
                )
            
            has_permission = await PermissionChecker.user_has_any_permission(
                db, current_user, list(permission_codes)
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required any of: {', '.join(permission_codes)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(*permission_codes: str):
    """
    Decorator to require all of the specified permissions.
    
    Usage:
        @router.post("/reconcile")
        @require_all_permissions("reconciliation.data.read", "reconciliation.data.update")
        async def reconcile_data(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db = kwargs.get('db')
            current_user = kwargs.get('current_user')
            
            if not db or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session or user not found in request context"
                )
            
            has_permission = await PermissionChecker.user_has_all_permissions(
                db, current_user, list(permission_codes)
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required all of: {', '.join(permission_codes)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

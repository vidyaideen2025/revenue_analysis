"""API endpoints for permission and role management."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import APIResponse
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User
from app.crud.permission import permission_repo, role_repo
from app.schemas.permission import (
    Permission,
    PermissionListResponse,
    Role,
    RoleCreate,
    RoleUpdate,
    RoleListResponse,
    UserPermissionsResponse
)
from app.utils.permissions import PermissionChecker

router = APIRouter()


@router.get("/me/permissions", response_model=None)
async def get_my_permissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> JSONResponse:
    """
    Get current user's permissions.
    
    **For Frontend Use**: Returns all permissions the user has access to.
    Frontend can use this to show/hide UI elements.
    
    **Authenticated users only**
    """
    # Get user's permissions
    permissions = await PermissionChecker.get_user_permissions(db, current_user)
    
    # Get role name
    role_map = {1: "ADMIN", 2: "OPERATIONS", 3: "CXO"}
    role_code = role_map.get(current_user.role, "UNKNOWN")
    
    return APIResponse.success(
        message="User permissions retrieved successfully",
        data={
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "role": current_user.role
            },
            "role": {
                "code": role_code,
                "value": current_user.role
            },
            "permissions": [p.code for p in permissions],
            "permission_details": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "category": p.category,
                    "action": p.action,
                    "resource": p.resource,
                    "description": p.description
                }
                for p in permissions
            ]
        }
    )


@router.get("/permissions", response_model=None)
async def list_permissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records"),
    category: str | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(None, description="Filter by active status")
) -> JSONResponse:
    """
    List all available permissions.
    
    **Admin only**
    
    Used by admin UI to show available permissions when creating/editing roles.
    """
    permissions = await permission_repo.get_all(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active
    )
    
    total = await permission_repo.count(
        db=db,
        category=category,
        is_active=is_active
    )
    
    # Group by category for easier UI display
    grouped_permissions = {}
    for perm in permissions:
        if perm.category not in grouped_permissions:
            grouped_permissions[perm.category] = []
        grouped_permissions[perm.category].append({
            "id": str(perm.id),
            "code": perm.code,
            "name": perm.name,
            "description": perm.description,
            "action": perm.action,
            "resource": perm.resource,
            "is_active": perm.is_active
        })
    
    return APIResponse.success(
        message="Permissions retrieved successfully",
        data={
            "items": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "action": p.action,
                    "resource": p.resource,
                    "is_active": p.is_active,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat()
                }
                for p in permissions
            ],
            "grouped": grouped_permissions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/roles", response_model=None)
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    include_system: bool = Query(True, description="Include system roles")
) -> JSONResponse:
    """
    List all roles with their permissions.
    
    **Admin only**
    
    Returns all roles including system roles (ADMIN, CXO, OPERATIONS) and custom roles.
    """
    roles = await role_repo.get_all(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        include_system=include_system
    )
    
    total = await role_repo.count(
        db=db,
        is_active=is_active,
        include_system=include_system
    )
    
    return APIResponse.success(
        message="Roles retrieved successfully",
        data={
            "items": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "code": r.code,
                    "description": r.description,
                    "is_system_role": r.is_system_role,
                    "is_active": r.is_active,
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                    "permissions": [
                        {
                            "id": str(p.id),
                            "code": p.code,
                            "name": p.name,
                            "category": p.category
                        }
                        for p in r.permissions
                    ],
                    "permission_count": len(r.permissions)
                }
                for r in roles
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/roles/{role_id}", response_model=None)
async def get_role(
    role_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Get a specific role with its permissions.
    
    **Admin only**
    """
    role = await role_repo.get_by_id(db, role_id)
    
    if not role:
        return APIResponse.not_found(
            message="Role not found",
            data={"detail": f"Role with ID {role_id} does not exist"}
        )
    
    return APIResponse.success(
        message="Role retrieved successfully",
        data={
            "id": str(role.id),
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_system_role": role.is_system_role,
            "is_active": role.is_active,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat(),
            "permissions": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "action": p.action,
                    "resource": p.resource
                }
                for p in role.permissions
            ]
        }
    )


@router.post("/roles", response_model=None, status_code=201)
async def create_role(
    role_in: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Create a new custom role with permissions.
    
    **Admin only**
    
    Example request body:
    ```json
    {
        "name": "Manager",
        "code": "MANAGER",
        "description": "Team manager with limited admin access",
        "permission_ids": [
            "uuid-1",
            "uuid-2"
        ]
    }
    ```
    """
    # Check if code already exists
    if await role_repo.code_exists(db, role_in.code):
        return APIResponse.bad_request(
            message="Role code already exists",
            data={"detail": f"A role with code '{role_in.code}' already exists", "field": "code"}
        )
    
    # Create role
    role = await role_repo.create(
        db=db,
        name=role_in.name,
        code=role_in.code,
        description=role_in.description,
        permission_ids=role_in.permission_ids
    )
    
    return APIResponse.created(
        message="Role created successfully",
        data={
            "id": str(role.id),
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_system_role": role.is_system_role,
            "is_active": role.is_active,
            "permissions": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "category": p.category
                }
                for p in role.permissions
            ]
        }
    )


@router.patch("/roles/{role_id}", response_model=None)
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Update a role's information and permissions.
    
    **Admin only**
    
    Note: System roles (ADMIN, CXO, OPERATIONS) cannot be deleted but can be modified.
    """
    role = await role_repo.get_by_id(db, role_id)
    
    if not role:
        return APIResponse.not_found(
            message="Role not found",
            data={"detail": f"Role with ID {role_id} does not exist"}
        )
    
    # Update role
    updated_role = await role_repo.update(
        db=db,
        role=role,
        name=role_in.name,
        description=role_in.description,
        is_active=role_in.is_active,
        permission_ids=role_in.permission_ids
    )
    
    return APIResponse.success(
        message="Role updated successfully",
        data={
            "id": str(updated_role.id),
            "name": updated_role.name,
            "code": updated_role.code,
            "description": updated_role.description,
            "is_system_role": updated_role.is_system_role,
            "is_active": updated_role.is_active,
            "permissions": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "category": p.category
                }
                for p in updated_role.permissions
            ]
        }
    )


@router.delete("/roles/{role_id}", response_model=None)
async def delete_role(
    role_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Delete a custom role.
    
    **Admin only**
    
    Note: System roles (ADMIN, CXO, OPERATIONS) cannot be deleted.
    """
    role = await role_repo.get_by_id(db, role_id)
    
    if not role:
        return APIResponse.not_found(
            message="Role not found",
            data={"detail": f"Role with ID {role_id} does not exist"}
        )
    
    if role.is_system_role:
        return APIResponse.bad_request(
            message="Cannot delete system role",
            data={"detail": "System roles (ADMIN, CXO, OPERATIONS) cannot be deleted"}
        )
    
    # Delete role
    await role_repo.delete(db, role)
    
    return APIResponse.success(
        message="Role deleted successfully",
        data={"id": str(role_id)}
    )

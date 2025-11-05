"""User management endpoints (Admin only, except GET by ID which supports self-access)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import APIResponse
from app.crud.user import user_repo
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate


router = APIRouter(tags=["Users"])


@router.get("/", response_model=None)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: str | None = Query(None, description="Search in email, username, full_name"),
    role: int | None = Query(None, description="Filter by role (1=ADMIN, 2=OPERATIONS, 3=CXO)"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    department_id: UUID | None = Query(None, description="Filter by department ID")
) -> JSONResponse:
    """
    List all users with pagination, search, and filtering.
    
    **Admin only**
    
    Query Parameters:
    - **skip**: Pagination offset (default: 0)
    - **limit**: Max results per page (default: 100, max: 100)
    - **search**: Search across email, username, full_name (case-insensitive)
    - **role**: Filter by role (1=ADMIN, 2=OPERATIONS, 3=CXO)
    - **is_active**: Filter by active status (true/false)
    
    Example:
        ```
        GET /api/v1/users/?skip=0&limit=20&search=john&role=2&is_active=true
        ```
    """
    # Get users with filters
    users = await user_repo.get_all(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active,
        department_id=department_id
    )
    
    # Get total count with same filters
    total = await user_repo.count(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        department_id=department_id
    )
    
    # Convert to schemas with department info
    from app.schemas.user import User as UserSchema
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "department_id": user.department_id,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "department_name": user.department_rel.name if user.department_rel else None,
            "department_code": user.department_rel.code if user.department_rel else None
        }
        user_list.append(UserSchema(**user_dict))
    
    return APIResponse.success(
        message="Users retrieved successfully",
        data={
            "items": [user.model_dump() for user in user_list],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{user_id}", response_model=None)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> JSONResponse:
    """
    Get a specific user by ID.
    
    **Access Control**:
    - **Admin**: Can view any user's profile
    - **Non-admin**: Can only view their own profile
    
    **Use cases**: User profile page, admin user management
    
    Example:
        ```
        GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000
        ```
    """
    # Check access control
    if current_user.role != UserRole.ADMIN.value and current_user.id != user_id:
        return APIResponse.forbidden(
            message="Forbidden",
            data={"detail": "You can only view your own profile"}
        )
    
    # Get user
    user = await user_repo.get_by_id(db, user_id)
    
    if not user:
        return APIResponse.not_found(
            message="User not found",
            data={"detail": f"User with ID {user_id} does not exist"}
        )
    
    # Convert to schema
    from app.schemas.user import User as UserSchema
    user_schema = UserSchema.model_validate(user)
    
    return APIResponse.success(
        message="User retrieved successfully",
        data=user_schema.model_dump()
    )


@router.post("/", response_model=None)
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Create a new user.
    
    **Admin only**
    
    Request Body:
        ```json
        {
            "email": "user@example.com",
            "username": "username",
            "full_name": "Full Name",
            "password": "SecurePass@123",
            "role": 2
        }
        ```
    
    Validation:
    - Email must be unique
    - Username must be unique
    - Password must be at least 8 characters
    - Role must be 1 (ADMIN), 2 (OPERATIONS), or 3 (CXO)
    """
    # Check if email already exists
    if await user_repo.email_exists(db, user_in.email):
        return APIResponse.bad_request(
            message="Email already exists",
            data={"detail": f"A user with email {user_in.email} already exists", "field": "email"}
        )
    
    # Check if username already exists
    if await user_repo.username_exists(db, user_in.username):
        return APIResponse.bad_request(
            message="Username already exists",
            data={"detail": f"A user with username {user_in.username} already exists", "field": "username"}
        )
    
    # Validate department if provided
    if user_in.department_id:
        from app.crud.department import department_repo
        department = await department_repo.get_by_id(db, user_in.department_id)
        if not department:
            return APIResponse.bad_request(
                message="Invalid department",
                data={"detail": "Department not found", "field": "department_id"}
            )
        if not department.is_active:
            return APIResponse.bad_request(
                message="Invalid department",
                data={"detail": "Department is not active", "field": "department_id"}
            )
    
    # Create user
    created_user = await user_repo.create(db, user_in, created_by=current_user.id)
    
    # Convert to schema with department info
    from app.schemas.user import User as UserSchema
    user_dict = {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
        "full_name": created_user.full_name,
        "department_id": created_user.department_id,
        "role": created_user.role,
        "is_active": created_user.is_active,
        "created_at": created_user.created_at,
        "updated_at": created_user.updated_at,
        "department_name": created_user.department_rel.name if created_user.department_rel else None,
        "department_code": created_user.department_rel.code if created_user.department_rel else None
    }
    user_schema = UserSchema(**user_dict)
    
    return APIResponse.created(
        message="User created successfully",
        data=user_schema.model_dump()
    )


@router.patch("/{user_id}", response_model=None)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Update user information (partial update).
    
    **Admin only**
    
    Request Body (all fields optional):
        ```json
        {
            "email": "newemail@example.com",
            "username": "newusername",
            "full_name": "New Full Name",
            "password": "NewSecurePass@123",
            "role": 3,
            "is_active": false
        }
        ```
    """
    # Get existing user
    user = await user_repo.get_by_id(db, user_id)
    
    if not user:
        return APIResponse.not_found(
            message="User not found",
            data={"detail": f"User with ID {user_id} does not exist"}
        )
    
    # Check email uniqueness if being updated
    if user_in.email and user_in.email != user.email:
        if await user_repo.email_exists(db, user_in.email):
            return APIResponse.bad_request(
                message="Email already exists",
                data={"detail": f"A user with email {user_in.email} already exists", "field": "email"}
            )
    
    # Check username uniqueness if being updated
    if user_in.username and user_in.username != user.username:
        if await user_repo.username_exists(db, user_in.username):
            return APIResponse.bad_request(
                message="Username already exists",
                data={"detail": f"A user with username {user_in.username} already exists", "field": "username"}
            )
    
    # Update user
    updated_user = await user_repo.update(db, user, user_in, updated_by=current_user.id)
    
    # Convert to schema
    from app.schemas.user import User as UserSchema
    user_schema = UserSchema.model_validate(updated_user)
    
    return APIResponse.success(
        message="User updated successfully",
        data=user_schema.model_dump()
    )


@router.put("/{user_id}/status", response_model=None)
async def update_user_status(
    user_id: UUID,
    status_update: UserStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Update user status (activate or deactivate).
    
    **Admin only**
    
    Request Body:
        ```json
        {
            "is_active": true   // true to activate, false to deactivate
        }
        ```
    
    Business Rules:
    - Admin cannot deactivate themselves
    """
    # Prevent self-deactivation
    if user_id == current_user.id and not status_update.is_active:
        return APIResponse.bad_request(
            message="Cannot deactivate your own account",
            data={"detail": "Administrators cannot deactivate themselves. Please ask another admin."}
        )
    
    # Get user
    user = await user_repo.get_by_id(db, user_id)
    
    if not user:
        return APIResponse.not_found(
            message="User not found",
            data={"detail": f"User with ID {user_id} does not exist"}
        )
    
    # Update status
    user_update = UserUpdate(is_active=status_update.is_active)
    updated_user = await user_repo.update(db, user, user_update, updated_by=current_user.id)
    
    # Convert to schema
    from app.schemas.user import User as UserSchema
    user_schema = UserSchema.model_validate(updated_user)
    
    action = "activated" if status_update.is_active else "deactivated"
    
    return APIResponse.success(
        message=f"User {action} successfully",
        data=user_schema.model_dump()
    )


@router.delete("/{user_id}", response_model=None)
async def delete_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)]
) -> JSONResponse:
    """
    Soft delete a user.
    
    **Admin only**
    
    Business Rules:
    - Admin cannot delete themselves
    - Soft delete preserves user record for audit trail
    - Deleted users cannot log in
    - Deleted users are excluded from normal queries
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        return APIResponse.bad_request(
            message="Cannot delete your own account",
            data={"detail": "Administrators cannot delete themselves. Please ask another admin."}
        )
    
    # Get user
    user = await user_repo.get_by_id(db, user_id)
    
    if not user:
        return APIResponse.not_found(
            message="User not found",
            data={"detail": f"User with ID {user_id} does not exist"}
        )
    
    # Check if already deleted
    if user.is_deleted:
        return APIResponse.bad_request(
            message="User already deleted",
            data={"detail": "This user has already been deleted"}
        )
    
    # Soft delete
    await user_repo.delete(db, user, deleted_by=current_user.id)
    
    return APIResponse.success(
        message="User deleted successfully",
        data={
            "id": str(user.id),
            "email": user.email,
            "is_deleted": True
        }
    )

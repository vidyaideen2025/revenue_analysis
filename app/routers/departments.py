"""Department management API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.crud.department import department_repo
from app.schemas.department import (
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentListResponse
)


router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=DepartmentListResponse)
async def list_departments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    search: str | None = Query(None, description="Search in department name or code"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all departments with filtering and pagination.
    
    **Admin only**
    
    Returns paginated list of departments with optional filters.
    
    Example:
    ```
    GET /api/v1/departments/?skip=0&limit=100&is_active=true
    ```
    """
    # Get departments
    departments = await department_repo.get_all(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )
    
    # Get total count
    total = await department_repo.count(
        db=db,
        search=search,
        is_active=is_active
    )
    
    # Add user count to each department
    items = []
    for dept in departments:
        user_count = await department_repo.get_user_count(db, dept.id)
        dept_dict = Department.model_validate(dept).model_dump()
        dept_dict['user_count'] = user_count
        items.append(Department(**dept_dict))
    
    return DepartmentListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{department_id}", response_model=Department)
async def get_department(
    department_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific department by ID.
    
    **Admin only**
    
    Returns detailed information about a specific department including user count.
    
    Example:
    ```
    GET /api/v1/departments/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    department = await department_repo.get_by_id(db, department_id)
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Add user count
    user_count = await department_repo.get_user_count(db, department.id)
    dept_dict = Department.model_validate(department).model_dump()
    dept_dict['user_count'] = user_count
    
    return Department(**dept_dict)


@router.post("/", response_model=Department, status_code=201)
async def create_department(
    department_in: DepartmentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new department.
    
    **Admin only**
    
    Creates a new department with the provided information.
    
    Example:
    ```json
    POST /api/v1/departments/
    {
        "name": "Information Technology",
        "code": "IT",
        "description": "Manages technology infrastructure and systems",
        "is_active": true
    }
    ```
    """
    # Check if code already exists
    existing = await department_repo.get_by_code(db, department_in.code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Department with code '{department_in.code}' already exists"
        )
    
    # Create department
    department = await department_repo.create(db, department_in)
    
    # Add user count (will be 0 for new department)
    dept_dict = Department.model_validate(department).model_dump()
    dept_dict['user_count'] = 0
    
    return Department(**dept_dict)


@router.patch("/{department_id}", response_model=Department)
async def update_department(
    department_id: UUID,
    department_in: DepartmentUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update department information.
    
    **Admin only**
    
    Updates only the provided fields (partial update).
    
    Example:
    ```json
    PATCH /api/v1/departments/550e8400-e29b-41d4-a716-446655440000
    {
        "description": "Updated description",
        "is_active": false
    }
    ```
    """
    # Get existing department
    department = await department_repo.get_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check code uniqueness if code is being updated
    if department_in.code:
        existing = await department_repo.get_by_code(
            db,
            department_in.code,
            exclude_id=department_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Department with code '{department_in.code}' already exists"
            )
    
    # Update department
    updated_department = await department_repo.update(db, department, department_in)
    
    # Add user count
    user_count = await department_repo.get_user_count(db, updated_department.id)
    dept_dict = Department.model_validate(updated_department).model_dump()
    dept_dict['user_count'] = user_count
    
    return Department(**dept_dict)


@router.delete("/{department_id}", response_model=dict)
async def delete_department(
    department_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a department.
    
    **Admin only**
    
    Soft deletes a department. Cannot delete departments with assigned users.
    
    Example:
    ```
    DELETE /api/v1/departments/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    # Get existing department
    department = await department_repo.get_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if department has users
    user_count = await department_repo.get_user_count(db, department_id)
    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete department with {user_count} assigned user(s). "
                   "Please reassign users before deleting."
        )
    
    # Soft delete
    await department_repo.delete(db, department)
    
    return {
        "message": f"Department '{department.name}' deleted successfully",
        "department_id": str(department_id)
    }

"""CRUD operations for Department model."""

from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentRepository:
    """Repository for department CRUD operations."""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False
    ) -> list[Department]:
        """
        Get all departments with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for name or code
            is_active: Filter by active status
            include_deleted: Whether to include soft-deleted departments
            
        Returns:
            List of departments
        """
        query = select(Department)
        
        # Exclude soft-deleted by default
        if not include_deleted:
            query = query.where(Department.is_deleted == False)
        
        # Filter by active status
        if is_active is not None:
            query = query.where(Department.is_active == is_active)
        
        # Search in name and code
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Department.name.ilike(search_term),
                    Department.code.ilike(search_term)
                )
            )
        
        # Order by name and apply pagination
        query = query.order_by(Department.name).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        db: AsyncSession,
        search: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False
    ) -> int:
        """
        Count departments with optional filtering.
        
        Args:
            db: Database session
            search: Search term for name or code
            is_active: Filter by active status
            include_deleted: Whether to include soft-deleted departments
            
        Returns:
            Total count of departments
        """
        query = select(func.count(Department.id))
        
        # Exclude soft-deleted by default
        if not include_deleted:
            query = query.where(Department.is_deleted == False)
        
        # Filter by active status
        if is_active is not None:
            query = query.where(Department.is_active == is_active)
        
        # Search in name and code
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Department.name.ilike(search_term),
                    Department.code.ilike(search_term)
                )
            )
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def get_by_id(self, db: AsyncSession, department_id: UUID) -> Department | None:
        """
        Get department by ID.
        
        Args:
            db: Database session
            department_id: Department UUID
            
        Returns:
            Department if found and not deleted, None otherwise
        """
        query = select(Department).where(
            Department.id == department_id,
            Department.is_deleted == False
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_code(self, db: AsyncSession, code: str, exclude_id: UUID | None = None) -> Department | None:
        """
        Get department by code (case-insensitive).
        
        Args:
            db: Database session
            code: Department code
            exclude_id: Department ID to exclude from search (for updates)
            
        Returns:
            Department if found, None otherwise
        """
        query = select(Department).where(
            func.lower(Department.code) == code.lower(),
            Department.is_deleted == False
        )
        
        if exclude_id:
            query = query.where(Department.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, department_in: DepartmentCreate) -> Department:
        """
        Create a new department.
        
        Args:
            db: Database session
            department_in: Department creation data
            
        Returns:
            Created department
        """
        department = Department(
            name=department_in.name,
            code=department_in.code,
            description=department_in.description,
            is_active=department_in.is_active
        )
        
        db.add(department)
        await db.commit()
        await db.refresh(department)
        
        return department
    
    async def update(
        self,
        db: AsyncSession,
        department: Department,
        department_in: DepartmentUpdate
    ) -> Department:
        """
        Update a department.
        
        Args:
            db: Database session
            department: Existing department
            department_in: Update data
            
        Returns:
            Updated department
        """
        update_data = department_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(department, field, value)
        
        await db.commit()
        await db.refresh(department)
        
        return department
    
    async def delete(self, db: AsyncSession, department: Department) -> Department:
        """
        Soft delete a department.
        
        Args:
            db: Database session
            department: Department to delete
            
        Returns:
            Deleted department
        """
        department.is_deleted = True
        department.is_active = False
        
        await db.commit()
        await db.refresh(department)
        
        return department
    
    async def get_user_count(self, db: AsyncSession, department_id: UUID) -> int:
        """
        Get count of users in a department.
        
        Args:
            db: Database session
            department_id: Department UUID
            
        Returns:
            Number of users in the department
        """
        from app.models.user import User
        
        query = select(func.count(User.id)).where(
            User.department_id == department_id
        )
        
        result = await db.execute(query)
        return result.scalar() or 0


# Create a singleton instance
department_repo = DepartmentRepository()

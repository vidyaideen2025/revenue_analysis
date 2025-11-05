"""CRUD operations for Permission and Role models."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.models.permission import Permission, Role, role_permissions


class PermissionRepository:
    """Repository for Permission CRUD operations."""
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        is_active: bool | None = None
    ) -> list[Permission]:
        """Get all permissions with optional filtering."""
        query = select(Permission)
        
        if category:
            query = query.where(Permission.category == category)
        
        if is_active is not None:
            query = query.where(Permission.is_active == is_active)
        
        query = query.order_by(Permission.category, Permission.name)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def count(
        db: AsyncSession,
        category: str | None = None,
        is_active: bool | None = None
    ) -> int:
        """Count permissions with filters."""
        query = select(func.count(Permission.id))
        
        if category:
            query = query.where(Permission.category == category)
        
        if is_active is not None:
            query = query.where(Permission.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalar_one()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, permission_id: UUID) -> Permission | None:
        """Get permission by ID."""
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Permission | None:
        """Get permission by code."""
        result = await db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()


class RoleRepository:
    """Repository for Role CRUD operations."""
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        include_system: bool = True
    ) -> list[Role]:
        """Get all roles with optional filtering."""
        query = select(Role).options(joinedload(Role.permissions))
        
        if is_active is not None:
            query = query.where(Role.is_active == is_active)
        
        if not include_system:
            query = query.where(Role.is_system_role == False)
        
        query = query.order_by(Role.name)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.unique().scalars().all())
    
    @staticmethod
    async def count(
        db: AsyncSession,
        is_active: bool | None = None,
        include_system: bool = True
    ) -> int:
        """Count roles with filters."""
        query = select(func.count(Role.id))
        
        if is_active is not None:
            query = query.where(Role.is_active == is_active)
        
        if not include_system:
            query = query.where(Role.is_system_role == False)
        
        result = await db.execute(query)
        return result.scalar_one()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: UUID) -> Role | None:
        """Get role by ID with permissions."""
        result = await db.execute(
            select(Role)
            .options(joinedload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Role | None:
        """Get role by code with permissions."""
        result = await db.execute(
            select(Role)
            .options(joinedload(Role.permissions))
            .where(Role.code == code)
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        description: str | None = None,
        permission_ids: list[UUID] | None = None
    ) -> Role:
        """Create a new role with permissions."""
        role = Role(
            name=name,
            code=code.upper(),
            description=description,
            is_system_role=False,
            is_active=True
        )
        
        # Add permissions if provided
        if permission_ids:
            permissions = await db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            role.permissions = list(permissions.scalars().all())
        
        db.add(role)
        await db.commit()
        await db.refresh(role, ["permissions"])
        
        return role
    
    @staticmethod
    async def update(
        db: AsyncSession,
        role: Role,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        permission_ids: list[UUID] | None = None
    ) -> Role:
        """Update role information and permissions."""
        if name is not None:
            role.name = name
        
        if description is not None:
            role.description = description
        
        if is_active is not None:
            role.is_active = is_active
        
        # Update permissions if provided
        if permission_ids is not None:
            permissions = await db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            role.permissions = list(permissions.scalars().all())
        
        await db.commit()
        await db.refresh(role, ["permissions"])
        
        return role
    
    @staticmethod
    async def delete(db: AsyncSession, role: Role) -> None:
        """Delete a role (only if not system role)."""
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        
        await db.delete(role)
        await db.commit()
    
    @staticmethod
    async def code_exists(db: AsyncSession, code: str, exclude_id: UUID | None = None) -> bool:
        """Check if role code already exists."""
        query = select(Role).where(func.upper(Role.code) == code.upper())
        
        if exclude_id:
            query = query.where(Role.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


# Create singleton instances
permission_repo = PermissionRepository()
role_repo = RoleRepository()

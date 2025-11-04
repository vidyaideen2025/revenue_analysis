"""CRUD operations for User model."""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    """Repository for User CRUD operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        """Get user by username."""
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def email_exists(db: AsyncSession, email: str) -> bool:
        """Check if email already exists."""
        user = await UserRepository.get_by_email(db, email)
        return user is not None
    
    @staticmethod
    async def username_exists(db: AsyncSession, username: str) -> bool:
        """Check if username already exists."""
        user = await UserRepository.get_by_username(db, username)
        return user is not None
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """Get all users with pagination."""
        result = await db.execute(
            select(User)
            .where(User.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate, created_by: UUID | None = None) -> User:
        """Create a new user."""
        password_hash = get_password_hash(user_in.password)
        
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            password_hash=password_hash,
            full_name=user_in.full_name,
            role=user_in.role,
            created_by=created_by,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        user_in: UserUpdate,
        updated_by: UUID | None = None
    ) -> User:
        """Update an existing user."""
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        # Set updated_by
        if updated_by:
            update_data["updated_by"] = updated_by
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user: User, deleted_by: UUID | None = None) -> None:
        """Soft delete a user."""
        user.is_deleted = True
        user.is_active = False
        if deleted_by:
            user.updated_by = deleted_by
        
        await db.commit()


# Global repository instance
user_repo = UserRepository()

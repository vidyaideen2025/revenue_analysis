"""Authentication service for user login and token management."""

from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.crud.user import user_repo
from app.models.user import User


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = await user_repo.get_by_email(db, email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def create_user_token(user: User) -> str:
        """
        Create JWT access token for a user.
        
        Args:
            user: User object
            
        Returns:
            JWT access token
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        token_data = {
            "sub": str(user.id),  # Convert UUID to string
            "email": user.email,
            "role": user.role,
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        return access_token


# Global service instance
auth_service = AuthService()

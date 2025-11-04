"""User model for authentication and authorization."""

import uuid
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.models.base import TimestampMixin


class UserRole(int, Enum):
    """User roles for RBAC."""
    ADMIN = 1
    OPERATIONS = 2
    CXO = 3


class Department(int, Enum):
    """User departments."""
    IT = 1
    FINANCE = 2
    OPERATIONS = 3
    AUDIT = 4
    HR = 5
    SALES = 6


class User(Base, TimestampMixin):
    """User model for authentication and role-based access control."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    department = Column(Integer, nullable=True)
    role = Column(Integer, nullable=False, default=UserRole.OPERATIONS.value)
    
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

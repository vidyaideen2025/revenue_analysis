"""User model for authentication and authorization."""

import uuid
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

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
    department = Column(Integer, nullable=True)  # Legacy field, will be removed after migration
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True, index=True)
    role = Column(Integer, nullable=False, default=UserRole.OPERATIONS.value)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationship to department
    department_rel = relationship("Department", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

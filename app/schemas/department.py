"""Pydantic schemas for Department model."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class DepartmentBase(BaseModel):
    """Base department schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Department name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique department code")
    description: str | None = Field(None, description="Department purpose and responsibilities")
    is_active: bool = Field(True, description="Whether the department is active")


class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating an existing department."""
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = None
    is_active: bool | None = None


class DepartmentInDB(DepartmentBase):
    """Schema for department data stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class Department(DepartmentInDB):
    """Schema for department response."""
    user_count: int | None = Field(None, description="Number of users in this department")


class DepartmentListResponse(BaseModel):
    """Schema for paginated department list response."""
    items: list[Department]
    total: int
    skip: int
    limit: int


class DepartmentSimple(BaseModel):
    """Simplified department schema for dropdowns and references."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    code: str

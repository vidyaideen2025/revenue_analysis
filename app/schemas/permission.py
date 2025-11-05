"""Pydantic schemas for Permission and Role models."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PermissionBase(BaseModel):
    """Base permission schema."""
    code: str = Field(..., description="Permission code (e.g., 'reconciliation.file.upload')")
    name: str = Field(..., description="Human-readable permission name")
    description: str | None = Field(None, description="Permission description")
    category: str = Field(..., description="Permission category")
    action: str = Field(..., description="Permission action (create, read, update, delete, execute)")
    resource: str = Field(..., description="Resource this permission applies to")


class Permission(PermissionBase):
    """Permission response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PermissionListResponse(BaseModel):
    """Response schema for paginated permission list."""
    items: list[Permission]
    total: int
    skip: int
    limit: int


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    code: str = Field(..., min_length=1, max_length=50, description="Role code (uppercase)")
    description: str | None = Field(None, max_length=255, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    permission_ids: list[UUID] = Field(default_factory=list, description="List of permission IDs to assign")


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    is_active: bool | None = None
    permission_ids: list[UUID] | None = Field(None, description="List of permission IDs to assign")


class RolePermissionSummary(BaseModel):
    """Simplified permission info for role response."""
    id: UUID
    code: str
    name: str
    category: str


class Role(RoleBase):
    """Role response schema with permissions."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[RolePermissionSummary] = []


class RoleListResponse(BaseModel):
    """Response schema for paginated role list."""
    items: list[Role]
    total: int
    skip: int
    limit: int


class UserPermissionsResponse(BaseModel):
    """Response schema for user's permissions (for frontend)."""
    user: dict = Field(..., description="User information")
    role: dict = Field(..., description="User's role information")
    permissions: list[str] = Field(..., description="List of permission codes user has access to")
    permission_details: list[Permission] = Field(..., description="Detailed permission information")

"""Pydantic schemas for Audit Log model."""

from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.audit_log import ActionType, ResourceType, AuditStatus, ErrorSeverity


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    action_type: ActionType
    description: str = Field(..., min_length=1)
    resource_type: ResourceType | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    status: AuditStatus = AuditStatus.SUCCESS
    severity: ErrorSeverity | None = None
    error_type: str | None = None
    stack_trace: str | None = None
    extra_data: dict[str, Any] | None = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log."""
    user_id: UUID | None = None


class AuditLogInDB(AuditLogBase):
    """Schema for audit log data stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    timestamp: datetime
    user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AuditLog(AuditLogInDB):
    """Schema for audit log response with user information."""
    user_email: str | None = None
    user_full_name: str | None = None


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs with pagination."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=200, description="Maximum number of records (default: 50, max: 200)")
    date_from: datetime | None = Field(None, description="Filter by start date (ISO 8601)")
    date_to: datetime | None = Field(None, description="Filter by end date (ISO 8601)")
    user_id: UUID | None = Field(None, description="Filter by user ID")
    action_type: ActionType | None = Field(None, description="Filter by action type")
    resource_type: ResourceType | None = Field(None, description="Filter by resource type")
    status: AuditStatus | None = Field(None, description="Filter by status")
    severity: ErrorSeverity | None = Field(None, description="Filter by error severity")
    error_type: str | None = Field(None, description="Filter by error type")
    search: str | None = Field(None, description="Search in description")


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list response."""
    items: list[AuditLog]
    total: int
    skip: int
    limit: int


class ErrorLogFilter(BaseModel):
    """Schema for filtering error logs specifically with pagination."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=200, description="Maximum number of records (default: 50, max: 200)")
    date_from: datetime | None = Field(None, description="Filter by start date (ISO 8601)")
    date_to: datetime | None = Field(None, description="Filter by end date (ISO 8601)")
    severity: ErrorSeverity | None = Field(None, description="Filter by error severity")
    error_type: str | None = Field(None, description="Filter by error type")
    search: str | None = Field(None, description="Search in description or stack trace")

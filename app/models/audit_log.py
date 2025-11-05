"""Audit log model for tracking all system actions and errors."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActionType(str, Enum):
    """Types of actions that can be logged."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    
    # Role & Permissions
    ROLE_ASSIGN = "role_assign"
    PERMISSION_CHANGE = "permission_change"
    
    # Data Operations
    DATA_UPLOAD = "data_upload"
    DATA_IMPORT = "data_import"
    DATA_EXPORT = "data_export"
    RECONCILIATION_RUN = "reconciliation_run"
    
    # System
    SETTING_CHANGE = "setting_change"
    SYSTEM_UPDATE = "system_update"
    
    # Errors
    ERROR_OCCURRED = "error_occurred"
    EXCEPTION_RAISED = "exception_raised"


class ResourceType(str, Enum):
    """Types of resources that can be affected."""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    DATA_FILE = "data_file"
    REPORT = "report"
    SETTING = "setting"
    SYSTEM = "system"


class AuditStatus(str, Enum):
    """Status of the audited action."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class ErrorSeverity(str, Enum):
    """Severity levels for error logs."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """Audit log model for tracking all system actions and errors."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=AuditStatus.SUCCESS.value)
    
    # Error-specific fields
    severity = Column(String(20), nullable=True, index=True)  # For error logs
    error_type = Column(String(255), nullable=True, index=True)  # Exception class name
    stack_trace = Column(Text, nullable=True)  # Full stack trace
    
    # Additional context
    extra_data = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action_type}, user_id={self.user_id}, status={self.status})>"

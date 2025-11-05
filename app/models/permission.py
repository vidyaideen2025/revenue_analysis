"""Permission and Role-Based Access Control models."""

import uuid
from enum import Enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class PermissionCategory(str, Enum):
    """Permission categories for organizing permissions."""
    RECONCILIATION = "reconciliation"
    DASHBOARD = "dashboard"
    REPORTS = "reports"
    USER_MANAGEMENT = "user_management"
    DEPARTMENT_MANAGEMENT = "department_management"
    SYSTEM = "system"


class PermissionAction(str, Enum):
    """Standard CRUD actions for permissions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"  # For special actions like file upload, validation


# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)


class Permission(Base, TimestampMixin):
    """Permission model for granular access control."""
    
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)  # PermissionCategory
    action = Column(String(50), nullable=False)  # PermissionAction
    resource = Column(String(100), nullable=False)  # e.g., "fine_data", "reconciliation", "dashboard"
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission(code={self.code}, resource={self.resource}, action={self.action})>"


class Role(Base, TimestampMixin):
    """Role model for grouping permissions."""
    
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)  # Cannot be deleted
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<Role(code={self.code}, name={self.name})>"


# Predefined permissions for the system
SYSTEM_PERMISSIONS = {
    # Reconciliation Permissions (Operations User)
    "reconciliation.file.upload": {
        "name": "Upload Files",
        "description": "Upload fine data files (Excel, CSV, JSON)",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.EXECUTE,
        "resource": "fine_data_file"
    },
    "reconciliation.data.read": {
        "name": "View Data Grid",
        "description": "View fine data grid and records",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.READ,
        "resource": "fine_data"
    },
    "reconciliation.data.update": {
        "name": "Edit Data Grid",
        "description": "Edit fine data records in grid",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.UPDATE,
        "resource": "fine_data"
    },
    "reconciliation.file.delete": {
        "name": "Delete Files",
        "description": "Delete uploaded fine data files",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.DELETE,
        "resource": "fine_data_file"
    },
    "reconciliation.summary.read": {
        "name": "View Reconciliation Summary",
        "description": "View reconciliation engine results and matching",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.READ,
        "resource": "reconciliation_summary"
    },
    "reconciliation.data.validate": {
        "name": "Validate Data",
        "description": "Run data validation checks",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.EXECUTE,
        "resource": "fine_data"
    },
    "reconciliation.data.submit": {
        "name": "Submit for Approval",
        "description": "Submit reconciliation data for approval",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.EXECUTE,
        "resource": "reconciliation_summary"
    },
    "reconciliation.ai.error_detection": {
        "name": "AI Error Detection",
        "description": "Access AI-powered error detection features",
        "category": PermissionCategory.RECONCILIATION,
        "action": PermissionAction.READ,
        "resource": "ai_error_detection"
    },
    
    # Dashboard Permissions (CXO User)
    "dashboard.executive.read": {
        "name": "View Executive Dashboard",
        "description": "Access executive dashboard with KPIs",
        "category": PermissionCategory.DASHBOARD,
        "action": PermissionAction.READ,
        "resource": "executive_dashboard"
    },
    "dashboard.revenue_trends.read": {
        "name": "View Revenue Trends",
        "description": "View revenue trend analysis and charts",
        "category": PermissionCategory.DASHBOARD,
        "action": PermissionAction.READ,
        "resource": "revenue_trends"
    },
    "dashboard.ai_insights.read": {
        "name": "View AI Insights",
        "description": "Access AI-powered insights and recommendations",
        "category": PermissionCategory.DASHBOARD,
        "action": PermissionAction.READ,
        "resource": "ai_insights"
    },
    "dashboard.collection_performance.read": {
        "name": "View Collection Performance",
        "description": "View collection performance metrics by emirate/week",
        "category": PermissionCategory.DASHBOARD,
        "action": PermissionAction.READ,
        "resource": "collection_performance"
    },
    
    # Reports Permissions
    "reports.export": {
        "name": "Export Reports",
        "description": "Export reports and data to various formats",
        "category": PermissionCategory.REPORTS,
        "action": PermissionAction.EXECUTE,
        "resource": "reports"
    },
    "reports.fine_issue.read": {
        "name": "View Fine Issue Report",
        "description": "View fine issue report data",
        "category": PermissionCategory.REPORTS,
        "action": PermissionAction.READ,
        "resource": "fine_issue_report"
    },
    "reports.fine_collection.read": {
        "name": "View Fine Collection Report",
        "description": "View fine collection report data",
        "category": PermissionCategory.REPORTS,
        "action": PermissionAction.READ,
        "resource": "fine_collection_report"
    },
    
    # User Management Permissions (Admin)
    "users.create": {
        "name": "Create Users",
        "description": "Create new user accounts",
        "category": PermissionCategory.USER_MANAGEMENT,
        "action": PermissionAction.CREATE,
        "resource": "users"
    },
    "users.read": {
        "name": "View Users",
        "description": "View user accounts and details",
        "category": PermissionCategory.USER_MANAGEMENT,
        "action": PermissionAction.READ,
        "resource": "users"
    },
    "users.update": {
        "name": "Update Users",
        "description": "Update user account information",
        "category": PermissionCategory.USER_MANAGEMENT,
        "action": PermissionAction.UPDATE,
        "resource": "users"
    },
    "users.delete": {
        "name": "Delete Users",
        "description": "Delete user accounts",
        "category": PermissionCategory.USER_MANAGEMENT,
        "action": PermissionAction.DELETE,
        "resource": "users"
    },
    
    # Department Management Permissions (Admin)
    "departments.create": {
        "name": "Create Departments",
        "description": "Create new departments",
        "category": PermissionCategory.DEPARTMENT_MANAGEMENT,
        "action": PermissionAction.CREATE,
        "resource": "departments"
    },
    "departments.read": {
        "name": "View Departments",
        "description": "View department information",
        "category": PermissionCategory.DEPARTMENT_MANAGEMENT,
        "action": PermissionAction.READ,
        "resource": "departments"
    },
    "departments.update": {
        "name": "Update Departments",
        "description": "Update department information",
        "category": PermissionCategory.DEPARTMENT_MANAGEMENT,
        "action": PermissionAction.UPDATE,
        "resource": "departments"
    },
    "departments.delete": {
        "name": "Delete Departments",
        "description": "Delete departments",
        "category": PermissionCategory.DEPARTMENT_MANAGEMENT,
        "action": PermissionAction.DELETE,
        "resource": "departments"
    },
    
    # System Permissions (Admin)
    "system.audit_logs.read": {
        "name": "View Audit Logs",
        "description": "Access system audit logs",
        "category": PermissionCategory.SYSTEM,
        "action": PermissionAction.READ,
        "resource": "audit_logs"
    },
    "system.settings.update": {
        "name": "Update System Settings",
        "description": "Modify system configuration",
        "category": PermissionCategory.SYSTEM,
        "action": PermissionAction.UPDATE,
        "resource": "system_settings"
    }
}


# Role definitions with their permissions
SYSTEM_ROLES = {
    "ADMIN": {
        "name": "Administrator",
        "description": "Full system access with all permissions",
        "permissions": [
            # All permissions
            *SYSTEM_PERMISSIONS.keys()
        ]
    },
    "CXO": {
        "name": "Chief Executive Officer",
        "description": "Executive dashboard and reporting access",
        "permissions": [
            # Dashboard access
            "dashboard.executive.read",
            "dashboard.revenue_trends.read",
            "dashboard.ai_insights.read",
            "dashboard.collection_performance.read",
            # Reports
            "reports.export",
            "reports.fine_issue.read",
            "reports.fine_collection.read",
            # Read-only reconciliation summary
            "reconciliation.summary.read",
        ]
    },
    "OPERATIONS": {
        "name": "Operations User",
        "description": "Reconciliation and data management access",
        "permissions": [
            # Reconciliation features
            "reconciliation.file.upload",
            "reconciliation.data.read",
            "reconciliation.data.update",
            "reconciliation.file.delete",
            "reconciliation.summary.read",
            "reconciliation.data.validate",
            "reconciliation.data.submit",
            "reconciliation.ai.error_detection",
            # Basic reports
            "reports.fine_issue.read",
            "reports.fine_collection.read",
        ]
    }
}

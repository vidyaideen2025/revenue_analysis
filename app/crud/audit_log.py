"""CRUD operations for Audit Log model."""

from datetime import datetime
from uuid import UUID
from sqlalchemy import select, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.audit_log import AuditLog, ActionType, ResourceType, AuditStatus, ErrorSeverity
from app.schemas.audit_log import AuditLogCreate


class AuditLogRepository:
    """Repository for audit log operations."""
    
    async def create(self, db: AsyncSession, audit_log_in: AuditLogCreate) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            db: Database session
            audit_log_in: Audit log data
            
        Returns:
            Created audit log
        """
        audit_log = AuditLog(
            user_id=audit_log_in.user_id,
            action_type=audit_log_in.action_type.value,
            resource_type=audit_log_in.resource_type.value if audit_log_in.resource_type else None,
            resource_id=audit_log_in.resource_id,
            description=audit_log_in.description,
            ip_address=audit_log_in.ip_address,
            user_agent=audit_log_in.user_agent,
            status=audit_log_in.status.value,
            severity=audit_log_in.severity.value if audit_log_in.severity else None,
            error_type=audit_log_in.error_type,
            stack_trace=audit_log_in.stack_trace,
            extra_data=audit_log_in.extra_data
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        return audit_log
    
    async def get_by_id(self, db: AsyncSession, audit_log_id: UUID) -> AuditLog | None:
        """
        Get audit log by ID.
        
        Args:
            db: Database session
            audit_log_id: Audit log ID
            
        Returns:
            Audit log or None if not found
        """
        result = await db.execute(
            select(AuditLog)
            .options(joinedload(AuditLog.user))
            .where(AuditLog.id == audit_log_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        user_id: UUID | None = None,
        action_type: ActionType | None = None,
        resource_type: ResourceType | None = None,
        status: AuditStatus | None = None,
        severity: ErrorSeverity | None = None,
        error_type: str | None = None,
        search: str | None = None
    ) -> list[AuditLog]:
        """
        Get all audit logs with filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return (default: 50, max: 200)
            date_from: Filter by start date
            date_to: Filter by end date
            user_id: Filter by user ID
            action_type: Filter by action type
            resource_type: Filter by resource type
            status: Filter by status
            severity: Filter by error severity
            error_type: Filter by error type
            search: Search in description
            
        Returns:
            List of audit logs
        """
        # Enforce maximum limit
        limit = min(limit, 200)
        
        query = select(AuditLog).options(joinedload(AuditLog.user))
        
        # Apply filters
        if date_from:
            query = query.where(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.where(AuditLog.timestamp <= date_to)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action_type:
            query = query.where(AuditLog.action_type == action_type.value)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type.value)
        if status:
            query = query.where(AuditLog.status == status.value)
        if severity:
            query = query.where(AuditLog.severity == severity.value)
        if error_type:
            query = query.where(AuditLog.error_type.ilike(f"%{error_type}%"))
        if search:
            query = query.where(AuditLog.description.ilike(f"%{search}%"))
        
        # Order by timestamp descending (most recent first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_error_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        severity: ErrorSeverity | None = None,
        error_type: str | None = None,
        search: str | None = None
    ) -> list[AuditLog]:
        """
        Get error logs only with efficient pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return (default: 50, max: 200)
            date_from: Filter by start date
            date_to: Filter by end date
            severity: Filter by error severity
            error_type: Filter by error type
            search: Search in description or stack trace
            
        Returns:
            List of error logs
        """
        # Enforce maximum limit for efficiency
        limit = min(limit, 200)
        
        query = select(AuditLog).options(joinedload(AuditLog.user))
        
        # Only get error status logs
        query = query.where(AuditLog.status == AuditStatus.ERROR.value)
        
        # Apply filters
        if date_from:
            query = query.where(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.where(AuditLog.timestamp <= date_to)
        if severity:
            query = query.where(AuditLog.severity == severity.value)
        if error_type:
            query = query.where(AuditLog.error_type.ilike(f"%{error_type}%"))
        if search:
            # Search in both description and stack trace
            query = query.where(
                or_(
                    AuditLog.description.ilike(f"%{search}%"),
                    AuditLog.stack_trace.ilike(f"%{search}%")
                )
            )
        
        # Order by timestamp descending (most recent errors first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        db: AsyncSession,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        user_id: UUID | None = None,
        action_type: ActionType | None = None,
        resource_type: ResourceType | None = None,
        status: AuditStatus | None = None,
        severity: ErrorSeverity | None = None,
        error_type: str | None = None,
        search: str | None = None
    ) -> int:
        """
        Count audit logs with filters.
        
        Args:
            db: Database session
            date_from: Filter by start date
            date_to: Filter by end date
            user_id: Filter by user ID
            action_type: Filter by action type
            resource_type: Filter by resource type
            status: Filter by status
            severity: Filter by error severity
            error_type: Filter by error type
            search: Search in description
            
        Returns:
            Total count of matching audit logs
        """
        query = select(func.count(AuditLog.id))
        
        # Apply same filters as get_all
        if date_from:
            query = query.where(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.where(AuditLog.timestamp <= date_to)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action_type:
            query = query.where(AuditLog.action_type == action_type.value)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type.value)
        if status:
            query = query.where(AuditLog.status == status.value)
        if severity:
            query = query.where(AuditLog.severity == severity.value)
        if error_type:
            query = query.where(AuditLog.error_type.ilike(f"%{error_type}%"))
        if search:
            query = query.where(AuditLog.description.ilike(f"%{search}%"))
        
        result = await db.execute(query)
        return result.scalar_one()
    
    async def count_errors(
        self,
        db: AsyncSession,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        severity: ErrorSeverity | None = None,
        error_type: str | None = None,
        search: str | None = None
    ) -> int:
        """
        Count error logs with filters.
        
        Args:
            db: Database session
            date_from: Filter by start date
            date_to: Filter by end date
            severity: Filter by error severity
            error_type: Filter by error type
            search: Search in description or stack trace
            
        Returns:
            Total count of matching error logs
        """
        query = select(func.count(AuditLog.id))
        
        # Only count error status logs
        query = query.where(AuditLog.status == AuditStatus.ERROR.value)
        
        # Apply same filters as get_error_logs
        if date_from:
            query = query.where(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.where(AuditLog.timestamp <= date_to)
        if severity:
            query = query.where(AuditLog.severity == severity.value)
        if error_type:
            query = query.where(AuditLog.error_type.ilike(f"%{error_type}%"))
        if search:
            query = query.where(
                or_(
                    AuditLog.description.ilike(f"%{search}%"),
                    AuditLog.stack_trace.ilike(f"%{search}%")
                )
            )
        
        result = await db.execute(query)
        return result.scalar_one()


# Create a singleton instance
audit_log_repo = AuditLogRepository()

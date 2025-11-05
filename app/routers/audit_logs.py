"""Audit logs API endpoints."""

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import APIResponse
from app.dependencies.auth import require_admin
from app.models.user import User
from app.models.audit_log import ActionType, ResourceType, AuditStatus, ErrorSeverity
from app.crud.audit_log import audit_log_repo
from app.schemas.audit_log import AuditLog, AuditLogListResponse, AuditLogFilter, ErrorLogFilter


router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    filters: AuditLogFilter = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List audit logs with filtering and pagination.
    
    **Admin only**
    
    Returns paginated list of audit logs with optional filters.
    
    Example:
    ```
    GET /api/v1/audit-logs/?skip=0&limit=50&action_type=user_create&date_from=2025-03-01T00:00:00Z
    ```
    """
    # Get audit logs
    audit_logs = await audit_log_repo.get_all(
        db=db,
        skip=filters.skip,
        limit=filters.limit,
        date_from=filters.date_from,
        date_to=filters.date_to,
        user_id=filters.user_id,
        action_type=filters.action_type,
        resource_type=filters.resource_type,
        status=filters.status,
        severity=filters.severity,
        error_type=filters.error_type,
        search=filters.search
    )
    
    # Get total count
    total = await audit_log_repo.count(
        db=db,
        date_from=filters.date_from,
        date_to=filters.date_to,
        user_id=filters.user_id,
        action_type=filters.action_type,
        resource_type=filters.resource_type,
        status=filters.status,
        severity=filters.severity,
        error_type=filters.error_type,
        search=filters.search
    )
    
    # Format response with user information
    items = []
    for log in audit_logs:
        item = AuditLog(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            action_type=ActionType(log.action_type),
            resource_type=ResourceType(log.resource_type) if log.resource_type else None,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            status=AuditStatus(log.status),
            severity=ErrorSeverity(log.severity) if log.severity else None,
            error_type=log.error_type,
            stack_trace=log.stack_trace,
            extra_data=log.extra_data,
            created_at=log.created_at,
            updated_at=log.updated_at,
            user_email=log.user.email if log.user else None,
            user_full_name=log.user.full_name if log.user else None
        )
        items.append(item)
    
    response_data = AuditLogListResponse(
        items=items,
        total=total,
        skip=filters.skip,
        limit=filters.limit
    )
    
    return response_data


@router.get("/errors", response_model=AuditLogListResponse)
async def list_error_logs(
    filters: ErrorLogFilter = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List error logs only with efficient pagination.
    
    **Admin only**
    
    Returns only audit logs with status='error', optimized for quick error review.
    
    **Efficiency Features:**
    - Default page size: 50 (optimized for quick loading)
    - Maximum page size: 200 (prevents excessive memory usage)
    - Indexed queries on severity and error_type
    - Includes full stack traces for debugging
    
    Example:
    ```
    GET /api/v1/audit-logs/errors?severity=error&limit=50
    ```
    """
    # Get error logs
    error_logs = await audit_log_repo.get_error_logs(
        db=db,
        skip=filters.skip,
        limit=filters.limit,
        date_from=filters.date_from,
        date_to=filters.date_to,
        severity=filters.severity,
        error_type=filters.error_type,
        search=filters.search
    )
    
    # Get total count
    total = await audit_log_repo.count_errors(
        db=db,
        date_from=filters.date_from,
        date_to=filters.date_to,
        severity=filters.severity,
        error_type=filters.error_type,
        search=filters.search
    )
    
    # Format response with user information
    items = []
    for log in error_logs:
        item = AuditLog(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            action_type=ActionType(log.action_type),
            resource_type=ResourceType(log.resource_type) if log.resource_type else None,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            status=AuditStatus(log.status),
            severity=ErrorSeverity(log.severity) if log.severity else None,
            error_type=log.error_type,
            stack_trace=log.stack_trace,
            extra_data=log.extra_data,
            created_at=log.created_at,
            updated_at=log.updated_at,
            user_email=log.user.email if log.user else None,
            user_full_name=log.user.full_name if log.user else None
        )
        items.append(item)
    
    response_data = AuditLogListResponse(
        items=items,
        total=total,
        skip=filters.skip,
        limit=filters.limit
    )
    
    return response_data


@router.get("/{audit_log_id}", response_model=AuditLog)
async def get_audit_log(
    audit_log_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific audit log by ID.
    
    **Admin only**
    
    Returns detailed information about a specific audit log including full metadata.
    
    Example:
    ```
    GET /api/v1/audit-logs/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    audit_log = await audit_log_repo.get_by_id(db, audit_log_id)
    
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    # Format response with user information
    item = AuditLog(
        id=audit_log.id,
        timestamp=audit_log.timestamp,
        user_id=audit_log.user_id,
        action_type=ActionType(audit_log.action_type),
        resource_type=ResourceType(audit_log.resource_type) if audit_log.resource_type else None,
        resource_id=audit_log.resource_id,
        description=audit_log.description,
        ip_address=audit_log.ip_address,
        user_agent=audit_log.user_agent,
        status=AuditStatus(audit_log.status),
        severity=ErrorSeverity(audit_log.severity) if audit_log.severity else None,
        error_type=audit_log.error_type,
        stack_trace=audit_log.stack_trace,
        extra_data=audit_log.extra_data,
        created_at=audit_log.created_at,
        updated_at=audit_log.updated_at,
        user_email=audit_log.user.email if audit_log.user else None,
        user_full_name=audit_log.user.full_name if audit_log.user else None
    )
    
    return item

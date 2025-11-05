"""Audit logging utility functions."""

import traceback
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import ActionType, ResourceType, AuditStatus, ErrorSeverity
from app.schemas.audit_log import AuditLogCreate
from app.crud.audit_log import audit_log_repo


def get_client_ip(request: Request) -> str | None:
    """
    Extract client IP address from request.
    
    Handles proxy headers like X-Forwarded-For.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address or None
    """
    # Check for proxy headers first
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    
    # Check for other proxy headers
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    if request.client:
        return request.client.host
    
    return None


async def log_audit(
    db: AsyncSession,
    user_id: UUID | None,
    action_type: ActionType,
    description: str,
    resource_type: ResourceType | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    status: AuditStatus = AuditStatus.SUCCESS,
    severity: ErrorSeverity | None = None,
    error_type: str | None = None,
    stack_trace: str | None = None,
    extra_data: dict | None = None
):
    """
    Log an audit event.
    
    Args:
        db: Database session
        user_id: ID of user who performed the action
        action_type: Type of action performed
        description: Human-readable description
        resource_type: Type of resource affected
        resource_id: ID of affected resource
        ip_address: IP address of the client
        user_agent: User agent string
        status: Status of the action
        severity: Error severity (for error logs)
        error_type: Exception class name (for error logs)
        stack_trace: Full stack trace (for error logs)
        extra_data: Additional context as dict
        
    Returns:
        Created audit log entry
    """
    try:
        audit_log_in = AuditLogCreate(
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            severity=severity,
            error_type=error_type,
            stack_trace=stack_trace,
            extra_data=extra_data
        )
        
        return await audit_log_repo.create(db, audit_log_in)
    except Exception as e:
        # Don't fail the request if audit logging fails
        print(f"Failed to create audit log: {e}")
        return None


async def log_login(
    db: AsyncSession,
    user_id: UUID,
    email: str,
    request: Request,
    success: bool = True
):
    """
    Log a login attempt.
    
    Args:
        db: Database session
        user_id: User ID
        email: User email
        request: HTTP request
        success: Whether login was successful
    """
    action_type = ActionType.LOGIN if success else ActionType.LOGIN_FAILED
    status = AuditStatus.SUCCESS if success else AuditStatus.FAILURE
    description = f"User {email} logged in successfully" if success else f"Failed login attempt for {email}"
    
    await log_audit(
        db=db,
        user_id=user_id if success else None,
        action_type=action_type,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        status=status
    )


async def log_logout(
    db: AsyncSession,
    user_id: UUID,
    email: str,
    request: Request
):
    """
    Log a logout event.
    
    Args:
        db: Database session
        user_id: User ID
        email: User email
        request: HTTP request
    """
    await log_audit(
        db=db,
        user_id=user_id,
        action_type=ActionType.LOGOUT,
        description=f"User {email} logged out",
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        status=AuditStatus.SUCCESS
    )


async def log_user_action(
    db: AsyncSession,
    current_user_id: UUID,
    action_type: ActionType,
    target_user_id: UUID,
    description: str,
    request: Request,
    extra_data: dict | None = None
):
    """
    Log a user management action.
    
    Args:
        db: Database session
        current_user_id: ID of user performing the action
        action_type: Type of action
        target_user_id: ID of user being affected
        description: Description of the action
        request: HTTP request
        extra_data: Additional context
    """
    await log_audit(
        db=db,
        user_id=current_user_id,
        action_type=action_type,
        resource_type=ResourceType.USER,
        resource_id=str(target_user_id),
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        extra_data=extra_data
    )


async def log_error(
    db: AsyncSession,
    error: Exception,
    description: str,
    user_id: UUID | None = None,
    request: Request | None = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR
):
    """
    Log an error/exception.
    
    Args:
        db: Database session
        error: The exception that occurred
        description: Human-readable description
        user_id: User who triggered the error (if applicable)
        request: HTTP request object (if applicable)
        severity: Error severity level
    """
    # Capture stack trace
    stack_trace_str = traceback.format_exc()
    
    # Build extra data
    extra_data = {
        "error_message": str(error),
        "error_class": error.__class__.__name__
    }
    
    if request:
        extra_data.update({
            "endpoint": str(request.url.path),
            "method": request.method,
            "query_params": dict(request.query_params)
        })
    
    await log_audit(
        db=db,
        user_id=user_id,
        action_type=ActionType.EXCEPTION_RAISED,
        description=description,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        status=AuditStatus.ERROR,
        severity=severity,
        error_type=error.__class__.__name__,
        stack_trace=stack_trace_str,
        extra_data=extra_data
    )


def determine_severity(error: Exception) -> ErrorSeverity:
    """
    Determine error severity based on exception type.
    
    Args:
        error: The exception
        
    Returns:
        Error severity level
    """
    # Critical errors
    if isinstance(error, (SystemError, MemoryError, RuntimeError)):
        return ErrorSeverity.CRITICAL
    
    # Validation errors are warnings
    if error.__class__.__name__ in ["ValidationError", "ValueError", "TypeError"]:
        return ErrorSeverity.WARNING
    
    # Default to ERROR
    return ErrorSeverity.ERROR

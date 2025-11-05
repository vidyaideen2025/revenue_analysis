"""Custom exceptions and exception handlers."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.response import APIResponse


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI validation errors.
    
    Catches Pydantic validation errors and returns standardized response.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return APIResponse.validation_error(
        message="Request validation failed",
        data={"errors": errors}
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return APIResponse.validation_error(
        message="Validation error",
        data={"errors": errors}
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    """
    return APIResponse.internal_error(
        message="Database error occurred",
        data={"error": str(exc)}
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle all other uncaught exceptions.
    
    Automatically logs errors to audit log system.
    """
    # Log the error to audit log
    try:
        from app.core.database import AsyncSessionLocal
        from app.utils.audit import log_error, determine_severity
        
        async with AsyncSessionLocal() as db:
            # Extract user ID if authenticated
            user_id = getattr(request.state, "user_id", None)
            
            # Determine severity
            severity = determine_severity(exc)
            
            # Log the error
            await log_error(
                db=db,
                error=exc,
                description=f"Unhandled exception: {exc.__class__.__name__}",
                user_id=user_id,
                request=request,
                severity=severity
            )
    except Exception as log_err:
        # Don't fail the request if logging fails
        print(f"Failed to log error to audit log: {log_err}")
    
    return APIResponse.internal_error(
        message="An unexpected error occurred",
        data={"error": str(exc)}
    )


class APIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)


async def api_exception_handler(
    request: Request,
    exc: APIException
) -> JSONResponse:
    """Handle custom API exceptions."""
    return APIResponse.error(
        message=exc.message,
        status_code=exc.status_code,
        data=exc.data
    )


class NotFoundException(APIException):
    """Exception for resource not found."""
    
    def __init__(self, message: str = "Resource not found", data: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )


class BadRequestException(APIException):
    """Exception for bad requests."""
    
    def __init__(self, message: str = "Bad request", data: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )


class UnauthorizedException(APIException):
    """Exception for unauthorized access."""
    
    def __init__(self, message: str = "Unauthorized", data: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            data=data
        )


class ForbiddenException(APIException):
    """Exception for forbidden access."""
    
    def __init__(self, message: str = "Forbidden", data: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            data=data
        )


class ConflictException(APIException):
    """Exception for resource conflicts."""
    
    def __init__(self, message: str = "Resource conflict", data: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            data=data
        )

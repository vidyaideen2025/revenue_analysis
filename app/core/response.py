"""Standardized API response structure."""

from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """Standardized API response wrapper."""
    
    @staticmethod
    def create_response(
        status_code: int,
        message: str,
        data: Any = None,
    ) -> JSONResponse:
        """
        Create a standardized API response.
        
        Args:
            status_code: HTTP status code
            message: Response message
            data: Response data (optional)
            
        Returns:
            JSONResponse with standardized structure
        """
        response_data = {
            "status": status_code,
            "message": message,
            "data": data if data is not None else []
        }
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create a success response."""
        return APIResponse.create_response(
            status_code=status_code,
            message=message,
            data=data
        )
    
    @staticmethod
    def created(
        message: str = "Resource created successfully",
        data: Any = None
    ) -> JSONResponse:
        """Create a 201 Created response."""
        return APIResponse.create_response(
            status_code=status.HTTP_201_CREATED,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Any = None
    ) -> JSONResponse:
        """Create an error response."""
        return APIResponse.create_response(
            status_code=status_code,
            message=message,
            data=data
        )
    
    @staticmethod
    def bad_request(
        message: str = "Bad request",
        data: Any = None
    ) -> JSONResponse:
        """Create a 400 Bad Request response."""
        return APIResponse.create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Unauthorized",
        data: Any = None
    ) -> JSONResponse:
        """Create a 401 Unauthorized response."""
        return APIResponse.create_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            data=data
        )
    
    @staticmethod
    def forbidden(
        message: str = "Forbidden",
        data: Any = None
    ) -> JSONResponse:
        """Create a 403 Forbidden response."""
        return APIResponse.create_response(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            data=data
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        data: Any = None
    ) -> JSONResponse:
        """Create a 404 Not Found response."""
        return APIResponse.create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            data=data
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation error",
        data: Any = None
    ) -> JSONResponse:
        """Create a 422 Validation Error response."""
        return APIResponse.create_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            data=data
        )
    
    @staticmethod
    def internal_error(
        message: str = "Internal server error",
        data: Any = None
    ) -> JSONResponse:
        """Create a 500 Internal Server Error response."""
        return APIResponse.create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            data=data
        )

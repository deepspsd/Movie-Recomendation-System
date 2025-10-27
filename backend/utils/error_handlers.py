"""
Enhanced Error Handling for Movie Recommendation System
Professional error handlers with detailed logging and user-friendly messages
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import JWTError
import logging
from typing import Union

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Exception for validation errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class AuthenticationException(AppException):
    """Exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(AppException):
    """Exception for authorization errors"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundException(AppException):
    """Exception for resource not found errors"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    """Exception for conflict errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}", extra={"errors": errors})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "details": errors,
            "path": request.url.path
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}", extra={
        "path": request.url.path,
        "type": type(exc).__name__
    })
    
    # Check for specific database errors
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Database constraint violation",
                "message": "The operation conflicts with existing data",
                "path": request.url.path
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "message": "An error occurred while processing your request",
            "path": request.url.path
        }
    )


async def jwt_exception_handler(request: Request, exc: JWTError):
    """Handle JWT errors"""
    logger.warning(f"JWT error: {str(exc)}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Authentication failed",
            "message": "Invalid or expired token",
            "path": request.url.path
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.exception(f"Unhandled exception: {str(exc)}", extra={
        "path": request.url.path,
        "type": type(exc).__name__
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "path": request.url.path
        }
    )


def register_error_handlers(app):
    """Register all error handlers with the FastAPI app"""
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import SQLAlchemyError
    from jose.exceptions import JWTError
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(JWTError, jwt_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")

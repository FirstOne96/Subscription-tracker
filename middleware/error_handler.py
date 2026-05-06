from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError


class NotFoundException(Exception):
    """Raised when a requested resource doesn't exist."""
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the app."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Pydantic raised a validation error — return 422 with structured details
        return JSONResponse(
            status_code=422,
            content={"success": False, "message": "Validation error", "errors": exc.errors()},
        )
    
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Duplicate field value entered"},
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": str(exc) or "Resource not found"},
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(exc)},
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Last-resort handler for anything we didn't anticipate
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error"},
        )
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and size limits."""
    
    def __init__(
        self,
        app,
        max_body_size: int = 1024 * 1024,  # 1 MB default
        allowed_content_types: list[str] = None,
    ):
        super().__init__(app)
        self.max_body_size = max_body_size
        self.allowed_content_types = allowed_content_types or ["application/json"]
    
    async def dispatch(self, request: Request, call_next):
        # Check content type for POST/PUT/PATCH
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type for ct in self.allowed_content_types):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"detail": f"Unsupported content type. Allowed: {self.allowed_content_types}"},
                )
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_body_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": f"Request body too large. Maximum size: {self.max_body_size} bytes"},
                    )
            except ValueError:
                pass
        
        # For JSON requests, validate JSON structure
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    # Read body to validate JSON
                    body = await request.body()
                    if body:
                        json.loads(body.decode())
                except json.JSONDecodeError:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Invalid JSON in request body"},
                    )
        
        response = await call_next(request)
        return response
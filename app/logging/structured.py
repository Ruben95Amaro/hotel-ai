import logging
import json
import sys
import uuid
from typing import Any
from datetime import datetime
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter with correlation ID support."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get correlation ID from context
        correlation_id = correlation_id_var.get()
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "name", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info"]:
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


def setup_structured_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging for the application."""
    
    handlers = []
    
    if log_format.lower() == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        handlers.append(handler)
    else:
        # Human-readable format
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(correlation_id)s] %(name)s: %(message)s",
                defaults={"correlation_id": "-"},
            )
        )
        handlers.append(handler)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True,
    )


class CorrelationIdMiddleware:
    """Middleware to extract/set correlation ID for each request."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract correlation ID from headers
        correlation_id = None
        for header_name, header_value in scope.get("headers", []):
            if header_name.decode().lower() == "x-correlation-id":
                correlation_id = header_value.decode()
                break
        
        # Generate if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
        
        # Set in context
        token = correlation_id_var.set(correlation_id)
        
        # Add to response headers
        async def send_with_correlation(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-correlation-id", correlation_id.encode()))
                message["headers"] = headers
            await send(message)
        
        try:
            await self.app(scope, receive, send_with_correlation)
        finally:
            correlation_id_var.reset(token)


def get_correlation_id() -> str | None:
    """Get the current correlation ID from context."""
    return correlation_id_var.get()
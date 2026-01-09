"""
Custom exceptions for HDR UK Gateway API client.
"""

from typing import Optional, Dict, Any


class GatewayAPIError(Exception):
    """Base exception for Gateway API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_url = request_url

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.request_url:
            parts.append(f"URL: {self.request_url}")
        return " ".join(parts)


class GatewayAuthError(GatewayAPIError):
    """Authentication or authorization error."""

    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class GatewayNotFoundError(GatewayAPIError):
    """Resource not found error."""

    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, status_code=404, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class GatewayRateLimitError(GatewayAPIError):
    """Rate limit exceeded error."""

    def __init__(self, retry_after: Optional[int] = None, **kwargs):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class GatewayValidationError(GatewayAPIError):
    """Request validation error."""

    def __init__(self, errors: Dict[str, Any], **kwargs):
        message = "Validation error"
        super().__init__(message, status_code=422, **kwargs)
        self.validation_errors = errors


class GatewayServerError(GatewayAPIError):
    """Server-side error."""

    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class GatewayTimeoutError(GatewayAPIError):
    """Request timeout error."""

    def __init__(self, timeout: float, **kwargs):
        message = f"Request timed out after {timeout} seconds"
        super().__init__(message, status_code=408, **kwargs)
        self.timeout = timeout


class GatewayConnectionError(GatewayAPIError):
    """Network connection error."""

    def __init__(self, message: str = "Failed to connect to Gateway API", **kwargs):
        super().__init__(message, **kwargs)

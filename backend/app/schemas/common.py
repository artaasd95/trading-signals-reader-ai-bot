#!/usr/bin/env python3
"""
Common Schemas

Shared Pydantic models for common data structures.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator

# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    """
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Sort order")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v.lower() if v else "asc"
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    """
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class ErrorDetail(BaseModel):
    """
    Error detail information.
    """
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field(description="Main error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "message": "Validation failed",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "code": "INVALID_EMAIL"
                    }
                ],
                "code": "VALIDATION_ERROR",
                "timestamp": "2024-01-01T12:00:00Z",
                "request_id": "req_123456789"
            }
        }


class SuccessResponse(BaseModel):
    """
    Standard success response format.
    """
    success: bool = Field(True, description="Indicates successful operation")
    message: str = Field(description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "123", "status": "active"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    Health check response format.
    """
    status: str = Field(description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(description="Application version")
    uptime: float = Field(description="Uptime in seconds")
    services: Dict[str, Dict[str, Any]] = Field(description="Service health status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.0.0",
                "uptime": 3600.0,
                "services": {
                    "database": {
                        "status": "healthy",
                        "response_time": 0.05,
                        "last_check": "2024-01-01T12:00:00Z"
                    },
                    "redis": {
                        "status": "healthy",
                        "response_time": 0.01,
                        "last_check": "2024-01-01T12:00:00Z"
                    },
                    "exchanges": {
                        "status": "healthy",
                        "connected": ["binance", "coinbase"],
                        "last_check": "2024-01-01T12:00:00Z"
                    }
                }
            }
        }


class FilterParams(BaseModel):
    """
    Common filtering parameters.
    """
    search: Optional[str] = Field(None, description="Search query")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    status: Optional[str] = Field(None, description="Filter by status")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v and 'date_from' in values and values['date_from']:
            if v < values['date_from']:
                raise ValueError('date_to must be after date_from')
        return v


class BulkOperationRequest(BaseModel):
    """
    Request for bulk operations.
    """
    ids: List[Union[UUID, str]] = Field(description="List of IDs to operate on")
    action: str = Field(description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")
    
    @validator('ids')
    def validate_ids_not_empty(cls, v):
        if not v:
            raise ValueError('ids list cannot be empty')
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 items at once')
        return v


class BulkOperationResponse(BaseModel):
    """
    Response for bulk operations.
    """
    total: int = Field(description="Total items processed")
    successful: int = Field(description="Successfully processed items")
    failed: int = Field(description="Failed items")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Operation results")


class FileUploadResponse(BaseModel):
    """
    File upload response.
    """
    filename: str = Field(description="Uploaded filename")
    size: int = Field(description="File size in bytes")
    content_type: str = Field(description="File content type")
    url: Optional[str] = Field(None, description="File access URL")
    checksum: Optional[str] = Field(None, description="File checksum")
    upload_id: str = Field(description="Upload identifier")


class ExportRequest(BaseModel):
    """
    Data export request.
    """
    format: str = Field("csv", regex="^(csv|json|xlsx)$", description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    fields: Optional[List[str]] = Field(None, description="Fields to include")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")


class ExportResponse(BaseModel):
    """
    Data export response.
    """
    export_id: str = Field(description="Export job identifier")
    status: str = Field(description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download expiration")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    record_count: Optional[int] = Field(None, description="Number of exported records")


class NotificationPreferences(BaseModel):
    """
    User notification preferences.
    """
    email_enabled: bool = Field(True, description="Enable email notifications")
    telegram_enabled: bool = Field(False, description="Enable Telegram notifications")
    push_enabled: bool = Field(True, description="Enable push notifications")
    trading_alerts: bool = Field(True, description="Trading alerts")
    ai_insights: bool = Field(True, description="AI insights notifications")
    market_updates: bool = Field(False, description="Market update notifications")
    system_alerts: bool = Field(True, description="System alert notifications")


class SystemMetrics(BaseModel):
    """
    System performance metrics.
    """
    cpu_usage: float = Field(description="CPU usage percentage")
    memory_usage: float = Field(description="Memory usage percentage")
    disk_usage: float = Field(description="Disk usage percentage")
    active_connections: int = Field(description="Active database connections")
    redis_memory: float = Field(description="Redis memory usage in MB")
    queue_size: int = Field(description="Background job queue size")
    response_time: float = Field(description="Average response time in ms")
    error_rate: float = Field(description="Error rate percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")


class APIKeyInfo(BaseModel):
    """
    API key information (without the actual key).
    """
    id: UUID = Field(description="API key ID")
    name: str = Field(description="API key name")
    prefix: str = Field(description="API key prefix (first 8 characters)")
    permissions: List[str] = Field(description="API key permissions")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(description="Whether the key is active")
    created_at: datetime = Field(description="Creation timestamp")


class RateLimitInfo(BaseModel):
    """
    Rate limit information.
    """
    limit: int = Field(description="Rate limit")
    remaining: int = Field(description="Remaining requests")
    reset_time: int = Field(description="Reset timestamp")
    window: int = Field(description="Time window in seconds")


class WebSocketMessage(BaseModel):
    """
    WebSocket message format.
    """
    type: str = Field(description="Message type")
    data: Dict[str, Any] = Field(description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    id: Optional[str] = Field(None, description="Message ID")
    channel: Optional[str] = Field(None, description="Channel name")


class BackupInfo(BaseModel):
    """
    Backup information.
    """
    id: str = Field(description="Backup ID")
    type: str = Field(description="Backup type")
    size: int = Field(description="Backup size in bytes")
    created_at: datetime = Field(description="Creation timestamp")
    status: str = Field(description="Backup status")
    file_path: Optional[str] = Field(None, description="Backup file path")
    checksum: Optional[str] = Field(None, description="Backup checksum")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
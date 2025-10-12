"""
Error response schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    field: Optional[str] = None
    message: str
    expected: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: Dict[str, Any]
    timestamp: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid birth date format",
                    "details": {
                        "field": "birth_date",
                        "expected": "YYYY-MM-DD"
                    }
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

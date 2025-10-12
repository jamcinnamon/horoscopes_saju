"""
Feedback schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class UserFeedback(BaseModel):
    """사용자 피드백"""
    request_id: str = Field(..., description="운세 요청 ID")
    rating: int = Field(..., ge=1, le=5, description="전체 만족도 (1-5)")
    accuracy: Optional[int] = Field(None, ge=1, le=5, description="정확도 (1-5)")
    feedback_text: Optional[str] = Field(None, description="자유 형식 피드백")
    categories: List[str] = Field(default_factory=list, description="피드백 카테고리")

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "rating": 4,
                "accuracy": 3,
                "feedback_text": "오늘의 운세가 정확했어요",
                "categories": ["today_fortune", "personality"]
            }
        }
    }


class FeedbackResponse(BaseModel):
    """피드백 응답"""
    success: bool
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "피드백이 저장되었습니다"
            }
        }
    }

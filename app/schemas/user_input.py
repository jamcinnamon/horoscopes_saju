"""
User input schemas
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from typing import Optional


class UserInput(BaseModel):
    """사용자 입력 데이터"""
    birth_date: date = Field(..., description="생년월일 (YYYY-MM-DD)")
    birth_time: Optional[time] = Field(None, description="출생 시간 (HH:MM)")
    timezone: str = Field(default="Asia/Seoul", description="타임존")

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v):
        """생년월일 검증"""
        from datetime import date as dt_date
        if v > dt_date.today():
            raise ValueError("생년월일은 미래 날짜일 수 없습니다")
        if v.year < 1900:
            raise ValueError("1900년 이후의 날짜를 입력해주세요")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "birth_date": "1990-05-15",
                "birth_time": "14:30",
                "timezone": "Asia/Seoul"
            }
        }
    }

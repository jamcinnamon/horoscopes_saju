"""
Saju related schemas
"""
from pydantic import BaseModel
from typing import Optional


class SajuInfo(BaseModel):
    """사주팔자 정보"""
    year_pillar: str  # 년주
    month_pillar: str  # 월주
    day_pillar: str  # 일주
    hour_pillar: Optional[str] = None  # 시주

    model_config = {
        "json_schema_extra": {
            "example": {
                "year_pillar": "경오",
                "month_pillar": "신사",
                "day_pillar": "갑인",
                "hour_pillar": "신미"
            }
        }
    }


class ElementBalance(BaseModel):
    """오행 균형"""
    wood: int = 0  # 목
    fire: int = 0  # 화
    earth: int = 0  # 토
    metal: int = 0  # 금
    water: int = 0  # 수

    model_config = {
        "json_schema_extra": {
            "example": {
                "wood": 2,
                "fire": 1,
                "earth": 3,
                "metal": 1,
                "water": 1
            }
        }
    }

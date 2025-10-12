"""
Fortune response schemas
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.saju import SajuInfo, ElementBalance


class TodayFortune(BaseModel):
    """오늘의 운세"""
    overall: str
    love: str
    career: str
    health: str
    lucky_number: int
    lucky_color: str


class YearFortune(BaseModel):
    """올해 운세"""
    overall: str
    career: str
    wealth: str
    relationships: str


class Personality(BaseModel):
    """성향 분석"""
    traits: List[str]
    strengths: List[str]
    weaknesses: List[str]
    element_balance: ElementBalance


class Fortune(BaseModel):
    """통합 운세 응답"""
    request_id: str
    zodiac_sign: str
    saju: SajuInfo
    today_fortune: TodayFortune
    year_fortune: YearFortune
    personality: Personality
    timestamp: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "zodiac_sign": "Taurus",
                "saju": {
                    "year_pillar": "경오",
                    "month_pillar": "신사",
                    "day_pillar": "갑인",
                    "hour_pillar": "신미"
                },
                "today_fortune": {
                    "overall": "오늘은 좋은 날입니다...",
                    "love": "사랑운이 좋습니다...",
                    "career": "직장운이 상승합니다...",
                    "health": "건강에 유의하세요...",
                    "lucky_number": 7,
                    "lucky_color": "Green"
                },
                "year_fortune": {
                    "overall": "올해는...",
                    "career": "커리어가...",
                    "wealth": "재물운이...",
                    "relationships": "인간관계가..."
                },
                "personality": {
                    "traits": ["성실함", "꼼꼼함"],
                    "strengths": ["책임감", "인내심"],
                    "weaknesses": ["고집", "완벽주의"],
                    "element_balance": {
                        "wood": 2,
                        "fire": 1,
                        "earth": 3,
                        "metal": 1,
                        "water": 1
                    }
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

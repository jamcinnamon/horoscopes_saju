"""
Saju interpretation database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SajuInterpretation(Base):
    """사주 해석 데이터"""
    __tablename__ = "saju_interpretations"

    id = Column(Integer, primary_key=True, index=True)
    element_pattern = Column(String(50), nullable=False, index=True)
    interpretation_type = Column(String(20), nullable=False)  # 'personality', 'fortune', 'career'
    interpretation_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SajuInterpretation(pattern={self.element_pattern}, type={self.interpretation_type})>"

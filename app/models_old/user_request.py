"""
User request logging model
"""
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class UserRequest(Base):
    """사용자 요청 로그"""
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, nullable=False, index=True)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time)
    zodiac_sign = Column(String(20))
    request_type = Column(String(20))  # 'complete', 'today', 'year', 'personality'
    response_data = Column(JSON)  # 생성된 운세 결과
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<UserRequest(id={self.request_id}, date={self.birth_date})>"

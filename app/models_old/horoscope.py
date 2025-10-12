"""
Horoscope database model
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Horoscope(Base):
    """별자리 운세 데이터"""
    __tablename__ = "horoscopes"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    zodiac_sign = Column(String(20), nullable=False, index=True)
    horoscope_text = Column(Text, nullable=False)
    love_text = Column(Text)
    lucky_number = Column(Integer)
    lucky_color = Column(String(20))
    source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Horoscope(date={self.date}, sign={self.zodiac_sign})>"

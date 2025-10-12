"""
User feedback model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserFeedback(Base):
    """사용자 피드백"""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), ForeignKey("user_requests.request_id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    accuracy = Column(Integer)
    feedback_text = Column(Text)
    categories = Column(JSON)  # ['today_fortune', 'personality']
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        CheckConstraint('accuracy IS NULL OR (accuracy >= 1 AND accuracy <= 5)', name='check_accuracy_range'),
    )

    def __repr__(self):
        return f"<UserFeedback(request_id={self.request_id}, rating={self.rating})>"

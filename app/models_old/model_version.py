"""
Model version tracking
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class ModelVersion(Base):
    """모델 버전 관리"""
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(20), nullable=False)  # 'horoscope', 'saju'
    version = Column(String(20), nullable=False)
    model_path = Column(String(255), nullable=False)
    performance_metrics = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ModelVersion(type={self.model_type}, version={self.version}, active={self.is_active})>"

from sqlalchemy import Column, Integer, Text, DateTime, Float, String
from sqlalchemy.sql import func
from app.models.base import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True)

    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)

    risk_level = Column(String(20))
    confidence = Column(Float)

    processing_time_ms = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
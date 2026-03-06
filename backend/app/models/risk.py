from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer)
    risk_level = Column(String(20))
    probability_score = Column(Float)
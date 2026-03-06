from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base

class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    article_number = Column(String(50))
    jurisdiction = Column(String(50))
    content = Column(Text)
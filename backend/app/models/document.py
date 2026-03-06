from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    doc_type = Column(String(50), nullable=False, index=True)
    version = Column(String(50), nullable=True)

    jurisdiction = Column(String(100), nullable=True, index=True)

    organization_id = Column(Integer, nullable=True, index=True)  # future multi-tenant

    source_url = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_doc_type_jurisdiction", "doc_type", "jurisdiction"),
    )
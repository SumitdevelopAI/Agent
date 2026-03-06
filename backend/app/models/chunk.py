from sqlalchemy import Column, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"), index=True)

    content = Column(Text, nullable=False)

    embedding = Column(Vector(384), nullable=False)

    token_count = Column(Integer, nullable=True)

    document = relationship("Document")

    __table_args__ = (
        Index("idx_chunk_document", "document_id"),
    )
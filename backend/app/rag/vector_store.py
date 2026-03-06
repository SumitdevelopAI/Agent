from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.chunk import Chunk




def add_documents(
    document_id: int,
    chunks: List[str],
    embeddings: List[List[float]]
):
    """
    Insert document chunks + embeddings into PostgreSQL (pgvector).
    """

    db: Session = SessionLocal()

    for text, embedding in zip(chunks, embeddings):
        chunk = Chunk(
            document_id=document_id,
            content=text,
            embedding=embedding
        )
        db.add(chunk)

def search_similar(
    query_embedding: list[float],
    top_k: int = 5,
    doc_type: str | None = None,
    document_id: int | None = None
):
    """
    Search for similar document chunks based on cosine similarity.
    Optional filtering by document type and/or specific document ID.
    """

    db: Session = SessionLocal()

    try:
        query = db.query(Chunk)

        if doc_type:
            query = query.join(Chunk.document).filter_by(doc_type=doc_type)

        if document_id:
            query = query.filter(Chunk.document_id == document_id)

        results = query.all()

        scored_results = []
        for chunk in results:
            similarity_score = chunk.embedding.cosine_distance(query_embedding)
            scored_results.append({
                "text": chunk.content,
                "similarity_score": similarity_score
            })

        scored_results.sort(key=lambda x: x["similarity_score"])

        return scored_results[:top_k]

    finally:
        db.close()

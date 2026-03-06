from app.rag.embeddings import embed_text
from app.rag.vector_store import search_similar

def retrieve_documents(query: str):
    embedding = embed_text(query)
    docs = search_similar(embedding)
    return docs
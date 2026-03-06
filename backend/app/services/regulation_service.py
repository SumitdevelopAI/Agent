import requests
from bs4 import BeautifulSoup
from app.database import SessionLocal
from app.models.document import Document
from app.models.chunk import Chunk
from app.rag.embeddings import embed_text


def ingest_regulation(url: str, jurisdiction: str, title: str):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 50]

    db = SessionLocal()

    doc = Document(
        name=title,
        doc_type="regulation",
        jurisdiction=jurisdiction,
        version="latest"
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    for block in text_blocks:
        embedding = embed_text(block)

        chunk = Chunk(
            document_id=doc.id,
            content=block,
            embedding=embedding
        )

        db.add(chunk)

    db.commit()
    db.close()

    return len(text_blocks)
from fastapi import APIRouter
from app.services.regulation_service import ingest_regulation

router = APIRouter()

@router.post("/ingest-regulation")
def ingest(url: str, jurisdiction: str, title: str):

    count = ingest_regulation(url, jurisdiction, title)

    return {
        "status": "ingested",
        "chunks": count
    }
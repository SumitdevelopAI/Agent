from fastapi import FastAPI
from app.models.base import Base
from app.database import engine

# Import models (for metadata registration)
from app.models.document import Document
from app.models.chunk import Chunk
from app.models.query_log import QueryLog
from app.models.regulation import Regulation
from app.models.risk import RiskAssessment

# Import routers
from app.routes import regulation, chat, upload

app = FastAPI(title="Compliance RAG API")


@app.on_event("startup")
def on_startup():
    """
    Create database tables safely at startup.
    """
    Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(regulation.router, tags=["Regulation"])


@app.get("/")
def root():
    return {"status": "Compliance RAG API running"}
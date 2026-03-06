# backend/app/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    document: str
    content: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    risk_level: str
    confidence: Optional[int] = None
    sources: List[Source] = []
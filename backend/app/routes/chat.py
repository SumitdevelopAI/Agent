from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.workflow import run_workflow

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_workflow(request.query)
    return result
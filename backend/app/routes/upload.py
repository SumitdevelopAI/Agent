from fastapi import APIRouter, UploadFile, File
from app.services.pdf_service import process_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    content = await file.read()

    if not file.filename:
        return {"error": "Filename missing"}

    chunks_count = process_pdf(content, file.filename)

    return {
        "status": "uploaded",
        "filename": file.filename,
        "chunks": chunks_count
    }
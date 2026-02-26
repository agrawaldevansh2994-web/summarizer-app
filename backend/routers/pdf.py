from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Literal
from services.pdf_service import summarize_pdf

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/summarize")
async def summarize_pdf_endpoint(
    file: UploadFile = File(...),
    style: Literal["bullet", "paragraph", "tldr"] = Form("bullet"),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="File too large. Max 50 MB.")

    try:
        result = summarize_pdf(file_bytes=file_bytes,
                               filename=file.filename, style=style)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

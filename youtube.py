from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from services.youtube_service import summarize_youtube_video

router = APIRouter()

class YouTubeRequest(BaseModel):
    url: str
    style: Literal["bullet", "paragraph", "tldr"] = "bullet"

@router.post("/summarize")
async def summarize_youtube(request: YouTubeRequest):
    try:
        result = summarize_youtube_video(url=request.url, style=request.style)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import ai_service

router = APIRouter()

class ResearchRequest(BaseModel):
    query: str
    depth: str = "standard"

@router.post("/")
async def research(request: ResearchRequest):
    result = await ai_service.research(request.query, request.depth)
    return result

@router.get("/topics")
async def get_trending_topics():
    return {
        "topics": [
            "Artificial Intelligence",
            "Machine Learning",
            "Technology Trends",
            "Science & Innovation"
        ]
    }

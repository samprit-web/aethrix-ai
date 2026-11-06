from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.aethrix_service import aethrix_model_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

class ReasonRequest(BaseModel):
    question: str

class CodeRequest(BaseModel):
    task: str
    language: str = "python"

class MathRequest(BaseModel):
    problem: str

@router.get("/status")
async def status():
    return {
        "model": "AETHRIX",
        "status": "operational" if aethrix_model_service.available else "initializing",
        "independent": True,
        "no_external_deps": True,
        "version": "1.0.0-alpha",
        "description": "Original AI model built from scratch"
    }

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = []
        for h in request.history:
            messages.append(h)
        messages.append({"role": "user", "content": request.message})
        
        response = await aethrix_model_service.chat_completion(
            messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {"response": response, "model": "AETHRIX", "source": "original"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reason")
async def reason(request: ReasonRequest):
    try:
        result = aethrix_model_service.engine.reason(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/code")
async def code(request: CodeRequest):
    try:
        result = await aethrix_model_service.generate_code(request.task, request.language)
        return {"code": result, "language": request.language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/math")
async def math(request: MathRequest):
    try:
        result = await aethrix_model_service.solve_math(request.problem)
        return {"solution": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research")
async def research(request: ReasonRequest):
    try:
        result = await aethrix_model_service.research(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

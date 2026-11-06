from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from ..inference.engine import AethrixInference
from ..core.config import AethrixConfig

app = FastAPI(
    title="AETHRIX API",
    description="Original, independent AI API - No third-party dependencies",
    version="1.0.0"
)

# Initialize AETHRIX
config = AethrixConfig()
engine = AethrixInference(config=config)

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    temperature: Optional[float] = 0.7
    max_length: Optional[int] = 512

class ChatResponse(BaseModel):
    response: str
    model: str = "AETHRIX-1.0"
    source: str = "original"

class ReasonRequest(BaseModel):
    question: str

class CodeRequest(BaseModel):
    task: str
    language: str = "python"

class MathRequest(BaseModel):
    problem: str

@app.get("/")
async def root():
    return {
        "name": "AETHRIX",
        "status": "operational",
        "description": "Original independent AI model",
        "independent": True,
        "no_external_deps": True
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "AETHRIX"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = engine.chat(
            request.message,
            request.history,
            temperature=request.temperature,
            max_length=request.max_length
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reason")
async def reason(request: ReasonRequest):
    try:
        result = engine.reason(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/code")
async def code(request: CodeRequest):
    try:
        result = engine.code(request.task, request.language)
        return {"code": result, "language": request.language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/math")
async def math(request: MathRequest):
    try:
        result = engine.solve_math(request.problem)
        return {"solution": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research")
async def research(request: ReasonRequest):
    try:
        result = engine.research(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

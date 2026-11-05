from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from app.services.ai_service import ai_service
from app.services.engine import safe_calc

router = APIRouter()

class CalcRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=600)

@router.get("/status")
async def engine_status():
    return {"engine": "aethrix-owned", **(ai_service.status() if hasattr(ai_service, 'status') else {})}

@router.post("/calc")
async def calc(req: CalcRequest):
    result = safe_calc(req.expression)
    return {"ok": result is not None, "expression": req.expression, "result": result, "engine": "aethrix-deterministic"}

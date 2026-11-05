import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.user import get_current_user_optional
from app.db.session import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.services.ai_service import ai_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    model: Optional[str] = None
    mode: str = "assistant"
    system: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[int] = None
    model: Optional[str] = None
    mode: str = "assistant"


def _serialize_conversation(c: Conversation):
    return {
        "id": c.id,
        "title": c.title,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


@router.get("/models")
async def list_models():
    detected = await ai_service.detect_ollama_models()
    models = ai_service.available_models()
    for name in detected:
        if not any(m["id"] == name for m in models):
            models.append({"id": name, "name": name, "provider": "ollama", "detected": True})
    return {"models": models, "default": ai_service.default_chat_model, "detected": detected}


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    conversation = None
    if request.conversation_id and current_user:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    elif current_user:
        conversation = Conversation(user_id=current_user.id, title=request.message[:60] or "New conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    chat_messages = []
    if conversation:
        db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
        db.commit()
        rows = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )
        chat_messages = [{"role": m.role, "content": m.content} for m in rows]
    else:
        for m in (request.history or [])[-20:]:
            role = m.get("role") if isinstance(m, dict) else None
            content = m.get("content") if isinstance(m, dict) else None
            if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
                chat_messages.append({"role": role, "content": content})
        chat_messages.append({"role": "user", "content": request.message})

    response = await ai_service.chat_completion(
        chat_messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        mode=request.mode,
        system=request.system,
    )

    if conversation:
        db.add(Message(conversation_id=conversation.id, role="assistant", content=response))
        conversation.title = conversation.title or request.message[:60]
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return ChatResponse(
        response=response,
        conversation_id=conversation.id if conversation else None,
        model=request.model or ai_service.default_chat_model,
        mode=request.mode,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, current_user: Optional[User] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    conversation = None
    if request.conversation_id and current_user:
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id).first()
    elif current_user:
        conversation = Conversation(user_id=current_user.id, title=request.message[:60] or "New conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    chat_messages = []
    if conversation:
        db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
        db.commit()
        rows = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at.asc(), Message.id.asc()).all()
        chat_messages = [{"role": m.role, "content": m.content} for m in rows]
    else:
        for m in (request.history or [])[-20:]:
            if isinstance(m, dict) and m.get("role") in {"user", "assistant"} and isinstance(m.get("content"), str):
                chat_messages.append({"role": m["role"], "content": m["content"]})
        chat_messages.append({"role": "user", "content": request.message})

    async def gen():
        full = []
        meta = {"conversation_id": conversation.id if conversation else None, "model": request.model or ai_service.default_chat_model, "mode": request.mode}
        yield f"data: {json.dumps({'type':'meta','data':meta})}\n\n"
        async for chunk in ai_service.stream_chat_completion(
            chat_messages, model=request.model, temperature=request.temperature, max_tokens=request.max_tokens, mode=request.mode, system=request.system
        ):
            full.append(chunk)
            yield f"data: {json.dumps({'type':'delta','data':chunk})}\n\n"
        text = "".join(full)
        if conversation:
            db.add(Message(conversation_id=conversation.id, role="assistant", content=text))
            db.add(conversation)
            db.commit()
        yield f"data: {json.dumps({'type':'done','data':meta})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/conversations")
def get_conversations(current_user: Optional[User] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not current_user:
        return []
    items = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        .limit(50)
        .all()
    )
    return [_serialize_conversation(c) for c in items]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    c = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.asc(), Message.id.asc()).all()
    return {**_serialize_conversation(c), "messages": [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat() if m.created_at else None} for m in msgs]}


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    c = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(c)
    db.commit()
    return {"status": "deleted"}

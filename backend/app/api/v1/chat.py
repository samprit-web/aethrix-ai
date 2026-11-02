from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.user import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.services.ai_service import ai_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: int = None
    model: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id, title=request.message[:50])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_message)
    
    # Get conversation history
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    chat_messages = [{"role": m.role, "content": m.content} for m in messages]
    
    # Get AI response
    response = await ai_service.chat_completion(chat_messages, model=request.model)
    
    # Save assistant message
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=response)
    db.add(assistant_message)
    db.commit()
    
    return ChatResponse(response=response, conversation_id=conversation.id)

@router.get("/conversations")
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()).all()
    return conversations

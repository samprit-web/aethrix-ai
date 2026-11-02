from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.user import get_current_user
from app.models.user import User
from app.models.email import EmailDraft
from app.services.ai_service import ai_service

router = APIRouter()

class EmailRequest(BaseModel):
    purpose: str
    recipient: str
    tone: str = "professional"
    details: str = ""

@router.post("/draft")
async def draft_email(request: EmailRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = await ai_service.generate_email(request.purpose, request.recipient, request.tone, request.details)
    
    # Parse subject and body from content (simple approach)
    lines = content.split('\n')
    subject = lines[0].replace('Subject:', '').strip() if lines and 'Subject' in lines[0] else "Email Draft"
    body = content
    
    draft = EmailDraft(
        user_id=current_user.id,
        subject=subject,
        recipient=request.recipient,
        body=body,
        tone=request.tone
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    
    return {"draft": draft, "content": content}

@router.get("/drafts")
def get_drafts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    drafts = db.query(EmailDraft).filter(EmailDraft.user_id == current_user.id).order_by(EmailDraft.created_at.desc()).all()
    return drafts

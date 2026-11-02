from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.user import get_current_user
from app.models.user import User
from app.models.document import Document
from app.services.ai_service import ai_service

router = APIRouter()

class DocumentRequest(BaseModel):
    doc_type: str = "report"
    topic: str
    requirements: str = ""

@router.post("/create")
async def create_document(request: DocumentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = await ai_service.create_document(request.doc_type, request.topic, request.requirements)
    
    document = Document(
        user_id=current_user.id,
        title=request.topic,
        content=content,
        doc_type=request.doc_type
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@router.get("/")
def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    documents = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    return documents

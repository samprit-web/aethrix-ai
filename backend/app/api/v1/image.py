from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.user import get_current_user
from app.models.user import User
from app.models.image import GeneratedImage
from app.services.ai_service import ai_service

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str
    model: str = None
    width: int = 1024
    height: int = 1024

@router.post("/generate")
async def generate_image(request: ImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await ai_service.generate_image(request.prompt, request.model, request.width, request.height)
    
    image = GeneratedImage(
        user_id=current_user.id,
        prompt=request.prompt,
        model=request.model or "stable-diffusion-xl",
        image_url=result.get("image_url")
    )
    db.add(image)
    db.commit()
    
    return result

@router.get("/history")
def get_image_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    images = db.query(GeneratedImage).filter(GeneratedImage.user_id == current_user.id).order_by(GeneratedImage.created_at.desc()).all()
    return images

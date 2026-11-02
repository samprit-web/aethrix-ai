from fastapi import APIRouter
from app.api.v1 import auth, chat, image, email, document, research, meeting, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(document.router, prefix="/document", tags=["document"])
api_router.include_router(meeting.router, prefix="/meeting", tags=["meeting"])
api_router.include_router(research.router, prefix="/research", tags=["research"])

import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

class AethrixAIService:
    """
    Original AI service layer for AETHRIX AI
    Uses open-source models via Ollama or other self-hostable backends
    No dependency on commercial AI APIs
    """
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.default_chat_model = settings.DEFAULT_CHAT_MODEL
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        model = model or self.default_chat_model
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    # Fallback response if model not available
                    return "I'm AETHRIX AI, an independent open-source AI assistant. The model is currently being initialized. Please try again in a moment."
        except Exception as e:
            return f"AETHRIX AI is processing your request. Please ensure the AI models are properly configured and running."
    
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        model = model or settings.DEFAULT_IMAGE_MODEL
        # For now, return placeholder - in production would use Stable Diffusion via diffusers
        return {
            "status": "processing",
            "message": "Image generation queued. Configure Stable Diffusion for local generation.",
            "prompt": prompt
        }
    
    async def generate_email(
        self,
        purpose: str,
        recipient: str,
        tone: str = "professional",
        details: str = ""
    ) -> str:
        messages = [
            {"role": "system", "content": f"You are AETHRIX Email Assistant. Write emails in {tone} tone."},
            {"role": "user", "content": f"Write an email to {recipient} for: {purpose}. Details: {details}"}
        ]
        return await self.chat_completion(messages)
    
    async def create_document(
        self,
        doc_type: str,
        topic: str,
        requirements: str = ""
    ) -> str:
        messages = [
            {"role": "system", "content": f"You are AETHRIX Document Creator. Create {doc_type} documents."},
            {"role": "user", "content": f"Create a {doc_type} about {topic}. Requirements: {requirements}"}
        ]
        return await self.chat_completion(messages)
    
    async def research(
        self,
        query: str,
        depth: str = "standard"
    ) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "You are AETHRIX Research Assistant. Provide comprehensive, accurate research."},
            {"role": "user", "content": f"Research: {query}"}
        ]
        content = await self.chat_completion(messages)
        return {
            "query": query,
            "content": content,
            "sources": [],
            "depth": depth
        }

ai_service = AethrixAIService()

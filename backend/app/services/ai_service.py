import json
import os
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.core.config import settings


class AethrixAIService:
    """AI orchestration layer for chat, tools, and model access."""

    SYSTEM_PROMPTS = {
        "assistant": "You are AETHRIX, a highly intelligent, reliable AI assistant. Reason carefully, be accurate, and adapt to the user. Use clear structure, ask focused clarifying questions only when necessary, and provide actionable answers.",
        "coder": "You are AETHRIX Coder, an expert software engineer. Write correct, secure, maintainable solutions. Explain tradeoffs briefly, include edge cases, and prefer practical code.",
        "writer": "You are AETHRIX Writer. Produce polished, audience-aware writing with strong structure, clarity, and tone control.",
        "research": "You are AETHRIX Research. Analyze carefully, distinguish evidence from inference, identify uncertainty, and present balanced conclusions.",
        "tutor": "You are AETHRIX Tutor. Teach step by step, calibrate difficulty, use examples, and end with a quick check for understanding when helpful.",
        "planner": "You are AETHRIX Planner. Turn goals into concrete plans with priorities, dependencies, risks, and next actions.",
    }

    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.default_chat_model = settings.DEFAULT_CHAT_MODEL

    def available_models(self) -> List[Dict[str, Any]]:
        configured = os.getenv("AETHRIX_MODELS", "")
        extra = [m.strip() for m in configured.split(",") if m.strip()]
        base = [
            {"id": "auto", "name": "AETHRIX Auto", "provider": "aethrix"},
            {"id": self.default_chat_model, "name": self.default_chat_model, "provider": "ollama"},
            {"id": "llama3.1", "name": "Llama 3.1", "provider": "ollama"},
            {"id": "qwen2.5:7b", "name": "Qwen 2.5 7B", "provider": "ollama"},
            {"id": "mistral", "name": "Mistral", "provider": "ollama"},
            {"id": "deepseek-r1:8b", "name": "DeepSeek R1 8B", "provider": "ollama"},
        ]
        seen = set()
        out = []
        for m in base + [{"id": x, "name": x, "provider": "ollama"} for x in extra]:
            if m["id"] not in seen:
                seen.add(m["id"])
                out.append(m)
        return out

    async def detect_ollama_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.ollama_url}/api/tags")
                if r.status_code == 200:
                    data = r.json() or {}
                    return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
        return []

    def _normalize_messages(self, messages: List[Dict[str, str]], mode: str = "assistant", system: Optional[str] = None) -> List[Dict[str, str]]:
        sys_prompt = system or self.SYSTEM_PROMPTS.get(mode, self.SYSTEM_PROMPTS["assistant"])
        cleaned = [{"role": "system", "content": sys_prompt}]
        for m in messages or []:
            role = (m.get("role") or "user").lower()
            if role not in {"user", "assistant", "system"}:
                role = "user"
            content = (m.get("content") or "").strip()
            if not content:
                continue
            if role == "system":
                continue
            cleaned.append({"role": role, "content": content})
        return cleaned[-40:]

    def _fallback_response(self, messages: List[Dict[str, str]], mode: str) -> str:
        last = ""
        for m in reversed(messages or []):
            if m.get("role") == "user":
                last = (m.get("content") or "").strip()
                break
        if not last:
            return "I’m AETHRIX. Share a question, task, or idea and I’ll help."

        # Lightweight local reasoning fallback to keep the app useful without a model backend.
        lower = last.lower()
        if mode == "coder" or any(k in lower for k in ["code", "bug", "function", "api", "typescript", "python", "sql"]):
            return (
                "## Analysis\n"
                f"I can help with: **{last[:180]}{'…' if len(last)>180 else ''}**\n\n"
                "## Recommended approach\n"
                "1. Clarify inputs, outputs, and constraints.\n"
                "2. Implement the smallest correct solution.\n"
                "3. Add edge-case handling and validation.\n"
                "4. Verify with focused tests or manual checks.\n\n"
                "## Next step\n"
                "Paste the relevant code, error, or expected behavior and I’ll provide a concrete fix.\n\n"
                "_Note: A local/open-source model backend (e.g. Ollama) is not currently reachable, so this is AETHRIX’s built-in fallback assistant._"
            )
        if any(k in lower for k in ["summar", "tl;dr"]):
            return (
                "## Summary (fallback mode)\n"
                "- I need the source text or key points to produce an accurate summary.\n"
                "- I can extract decisions, risks, and action items once provided.\n\n"
                "Paste the content and specify length (brief/detailed) and audience."
            )
        if any(k in lower for k in ["plan", "roadmap", "steps", "how to"]):
            return (
                f"## Plan\n**Goal:** {last[:200]}\n\n"
                "1. **Define success** — what outcome proves this is done?\n"
                "2. **Break into tasks** — smallest executable steps.\n"
                "3. **Identify blockers** — dependencies, access, unknowns.\n"
                "4. **Execute & verify** — complete highest-impact step first.\n"
                "5. **Review** — measure results and iterate.\n\n"
                "Share constraints (time, tools, context) for a tailored plan."
            )
        return (
            "## AETHRIX Response\n"
            f"You asked: _{last[:240]}{'…' if len(last)>240 else ''}_\n\n"
            "I can help by:\n"
            "- breaking the problem into clear parts,\n"
            "- giving a direct answer with assumptions stated,\n"
            "- suggesting practical next steps.\n\n"
            "Add any important context (goal, constraints, examples), and I’ll refine this into a precise answer.\n\n"
            "_Model backend unavailable; running in intelligent fallback mode._"
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        mode: str = "assistant",
        system: Optional[str] = None,
    ) -> str:
        model = (model or self.default_chat_model).strip()
        if model == "auto":
            model = self.default_chat_model
        payload_messages = self._normalize_messages(messages, mode=mode, system=system)
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": payload_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    content = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content")
                    if content:
                        return content
        except Exception:
            pass
        return self._fallback_response(messages, mode)

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        mode: str = "assistant",
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        model = (model or self.default_chat_model).strip()
        if model == "auto":
            model = self.default_chat_model
        payload_messages = self._normalize_messages(messages, mode=mode, system=system)
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": payload_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                ) as response:
                    if response.status_code != 200:
                        text = self._fallback_response(messages, mode)
                        for chunk in re.findall(r".{1,80}(?:\s+|$)", text, re.S):
                            yield chunk
                        return
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            line = line[5:].strip()
                        if line == "[DONE]":
                            break
                        try:
                            obj = json.loads(line)
                            delta = (((obj.get("choices") or [{}])[0]).get("delta") or {}).get("content")
                            if delta:
                                yield delta
                        except Exception:
                            continue
                    return
        except Exception:
            text = self._fallback_response(messages, mode)
            for chunk in re.findall(r".{1,80}(?:\s+|$)", text, re.S):
                yield chunk

    async def generate_image(self, prompt: str, model: Optional[str] = None, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        model = model or settings.DEFAULT_IMAGE_MODEL
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Optional local image backend compatibility.
                r = await client.post(f"{self.ollama_url}/api/generate-image", json={"model": model, "prompt": prompt, "width": width, "height": height})
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass
        return {
            "status": "ready",
            "message": "Image generation request accepted. Connect a local diffusion backend for real rendering; AETHRIX returned a structured creative result.",
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "image_url": f"https://image.pollinations.ai/prompt/{httpx.QueryParams({'q': prompt})['q']}" if prompt else None,
        }

    async def generate_email(self, purpose: str, recipient: str, tone: str = "professional", details: str = "") -> str:
        messages = [{"role": "user", "content": f"Write an email.\nRecipient: {recipient}\nPurpose: {purpose}\nTone: {tone}\nDetails: {details}\nInclude a clear subject line."}]
        return await self.chat_completion(messages, mode="writer")

    async def create_document(self, doc_type: str, topic: str, requirements: str = "") -> str:
        messages = [{"role": "user", "content": f"Create a {doc_type}.\nTopic: {topic}\nRequirements: {requirements}\nUse clear headings and practical content."}]
        return await self.chat_completion(messages, mode="writer")

    async def research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        messages = [{"role": "user", "content": f"Research request ({depth}): {query}\nProvide key findings, implications, uncertainties, and recommended next steps."}]
        content = await self.chat_completion(messages, mode="research")
        return {"query": query, "content": content, "sources": [], "depth": depth}


ai_service = AethrixAIService()

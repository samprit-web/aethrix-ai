import json
import logging
import os
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AethrixAIService:
    """AI orchestration with OpenAI-compatible provider support, Ollama fallback, and streaming."""

    SYSTEM_PROMPTS = {
        "assistant": (
            "You are AETHRIX, a highly intelligent, knowledgeable, and helpful AI assistant. "
            "Your top priorities are correctness, logical reasoning, clarity, and usefulness. "
            "Before answering, identify what the user is asking, resolve ambiguity from context when possible, and choose the most accurate approach. "
            "Think step by step for complex questions: check assumptions, verify logic, consider edge cases, and avoid unsupported claims. "
            "For factual topics, be precise; if you are uncertain, outdated, or lack sources, say so clearly and explain what is known. "
            "For math, coding, and technical problems, show the method, validate the result when practical, and provide working examples. "
            "Give elaborate answers when helpful, but keep them organized with headings, lists, tables, or code blocks. "
            "Adapt to the user's language and level, be conversational and respectful, and ask a brief clarifying question only when necessary."
        ),
        "coder": (
            "You are AETHRIX Coder, an expert software engineer. Provide correct, secure, maintainable, and well-explained solutions. "
            "Include code examples, edge cases, testing guidance, and tradeoffs. Prefer practical production-ready approaches."
        ),
        "writer": (
            "You are AETHRIX Writer. Produce polished, clear, audience-aware writing with strong structure and tone control. "
            "Revise as needed and explain choices briefly when helpful."
        ),
        "research": (
            "You are AETHRIX Research. Provide comprehensive, balanced analysis. Distinguish evidence from inference, note uncertainty, "
            "compare viewpoints when relevant, and end with actionable conclusions."
        ),
        "tutor": (
            "You are AETHRIX Tutor. Teach patiently and step by step, calibrate to the learner's level, use examples/analogies, "
            "check understanding, and suggest practice."
        ),
        "planner": (
            "You are AETHRIX Planner. Turn goals into concrete plans with priorities, sequencing, dependencies, risks, timelines, and next actions."
        ),
    }

    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")

    @property
    def default_chat_model(self) -> str:
        return settings.resolved_ai_model() or settings.DEFAULT_CHAT_MODEL

    def available_models(self) -> List[Dict[str, Any]]:
        configured = os.getenv("AETHRIX_MODELS", "")
        extra = [m.strip() for m in configured.split(",") if m.strip()]
        base = [{"id": "auto", "name": "Auto (Recommended)", "provider": "auto"}]
        resolved = settings.resolved_ai_model()
        if resolved:
            base.append({"id": resolved, "name": resolved, "provider": "configured"})
        for m in [settings.DEFAULT_CHAT_MODEL, "gpt-4o-mini", "gpt-4.1-mini", "claude-3.5-sonnet", "llama3.1", "qwen2.5:7b", "mistral", *extra]:
            if m and not any(x["id"] == m for x in base):
                base.append({"id": m, "name": m, "provider": "model"})
        return base

    async def detect_ollama_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.get(f"{self.ollama_url}/api/tags")
                if r.status_code == 200:
                    data = r.json() or {}
                    return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            return []
        return []

    def _normalize_messages(self, messages: List[Dict[str, str]], mode: str = "assistant", system: Optional[str] = None) -> List[Dict[str, str]]:
        sys_prompt = (system or "").strip() or self.SYSTEM_PROMPTS.get(mode, self.SYSTEM_PROMPTS["assistant"])
        cleaned = [{"role": "system", "content": sys_prompt}]
        for m in messages or []:
            if not isinstance(m, dict):
                continue
            role = str(m.get("role") or "user").lower()
            if role not in {"user", "assistant", "system"}:
                role = "user"
            content = str(m.get("content") or "").strip()
            if not content:
                continue
            if role == "system":
                continue
            cleaned.append({"role": role, "content": content})
        # Keep recent context; provider/model limits vary.
        if len(cleaned) > 61:
            cleaned = [cleaned[0]] + cleaned[-60:]
        return cleaned

    def _provider_candidates(self) -> List[Dict[str, str]]:
        candidates: List[Dict[str, str]] = []
        base = (settings.resolved_ai_base_url() or "").rstrip("/")
        key = settings.resolved_ai_api_key() or ""
        if base:
            # Try common OpenAI-compatible paths.
            bases = []
            for b in [base, base + "/v1" if not base.endswith("/v1") else base, base.replace("/v1", "")]:
                b = b.rstrip("/")
                if b and b not in bases:
                    bases.append(b)
            for b in bases:
                candidates.append({"type": "openai", "base": b, "key": key})
        # Ollama OpenAI-compatible endpoint
        candidates.append({"type": "ollama", "base": self.ollama_url, "key": ""})
        return candidates

    async def _openai_chat(self, client: httpx.AsyncClient, base: str, key: str, payload: Dict[str, Any]) -> Optional[str]:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        # Some gateways may not want /v1 prefix twice; try both.
        paths = ["/chat/completions", "/v1/chat/completions", "/api/v1/chat/completions"]
        tried = set()
        for path in paths:
            for b in [base.rstrip("/"), base.rstrip("/").replace("/v1", "")]:
                url = b.rstrip("/") + path
                if url in tried:
                    continue
                tried.add(url)
                try:
                    r = await client.post(url, json=payload, headers=headers)
                    if r.status_code == 200:
                        data = r.json()
                        content = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content")
                        if isinstance(content, str) and content.strip():
                            return content
                    # 401/403/404 may indicate wrong path or auth; continue trying candidates.
                except Exception:
                    continue
        return None

    async def _openai_stream(self, client: httpx.AsyncClient, base: str, key: str, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        paths = ["/chat/completions", "/v1/chat/completions", "/api/v1/chat/completions"]
        tried = set()
        for path in paths:
            for b in [base.rstrip("/"), base.rstrip("/").replace("/v1", "")]:
                url = b.rstrip("/") + path
                if url in tried:
                    continue
                tried.add(url)
                try:
                    async with client.stream("POST", url, json={**payload, "stream": True}, headers=headers) as r:
                        if r.status_code != 200:
                            continue
                        sent = False
                        async for line in r.aiter_lines():
                            if not line:
                                continue
                            if line.startswith("data:"):
                                line = line[5:].strip()
                            if line == "[DONE]":
                                if sent:
                                    return
                                break
                            try:
                                obj = json.loads(line)
                            except Exception:
                                continue
                            choice = (obj.get("choices") or [{}])[0]
                            delta = ((choice.get("delta") or {}).get("content")) or ((choice.get("message") or {}).get("content"))
                            if isinstance(delta, str) and delta:
                                sent = True
                                yield delta
                        if sent:
                            return
                except Exception:
                    continue
        return

    def has_provider_config(self) -> bool:
        return bool(settings.resolved_ai_base_url() or settings.resolved_ai_api_key() or settings.OLLAMA_BASE_URL)

    def status(self) -> Dict[str, Any]:
        base = settings.resolved_ai_base_url() or ""
        return {
            "ready": self.has_provider_config(),
            "model": self.default_chat_model,
            "provider_hint": "openai-compatible" if base else "ollama/local",
            "base_configured": bool(base),
            "key_configured": bool(settings.resolved_ai_api_key()),
        }

    def _setup_message(self, mode: str) -> str:
        return (
            "## AI setup required for live, accurate answers\n"
            "AETHRIX’s chat UI is deployed, but it needs a live language-model provider to answer questions correctly and logically across topics.\n\n"
            "**Set these Vercel/host environment variables (recommended: OpenAI-compatible):**\n"
            "- `AI_BASE_URL` — provider API base URL (OpenAI-compatible)\n"
            "- `AI_API_KEY` — provider API key\n"
            "- `AI_MODEL` — model name (choose a capable model for best accuracy)\n\n"
            "**Also supported:** `OPENAI_API_KEY` (+ optional `OPENAI_BASE_URL`, `AI_MODEL`), or OpenRouter/Groq/Together equivalents via `AI_BASE_URL`/`AI_API_KEY`. For self-hosting, use `OLLAMA_BASE_URL` and `DEFAULT_CHAT_MODEL`.\n\n"
            f"Current mode: **{mode}**. After setting variables, redeploy/restart the backend and send your question again."
        )

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4096, mode: str = "assistant", system: Optional[str] = None) -> str:
        model = (model or self.default_chat_model or "gpt-4o-mini").strip()
        if model == "auto":
            model = self.default_chat_model or "gpt-4o-mini"
        payload_messages = self._normalize_messages(messages, mode=mode, system=system)
        payload = {"model": model, "messages": payload_messages, "temperature": max(0.0, min(float(temperature or 0.7), 2.0)), "max_tokens": max(256, min(int(max_tokens or 4096), 8192))}
        timeout = httpx.Timeout(180.0, connect=15.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for cand in self._provider_candidates():
                content = await self._openai_chat(client, cand["base"], cand.get("key", ""), payload)
                if content:
                    return content
        return self._setup_message(mode)

    async def stream_chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4096, mode: str = "assistant", system: Optional[str] = None) -> AsyncGenerator[str, None]:
        model = (model or self.default_chat_model or "gpt-4o-mini").strip()
        if model == "auto":
            model = self.default_chat_model or "gpt-4o-mini"
        payload_messages = self._normalize_messages(messages, mode=mode, system=system)
        payload = {"model": model, "messages": payload_messages, "temperature": max(0.0, min(float(temperature or 0.7), 2.0)), "max_tokens": max(256, min(int(max_tokens or 4096), 8192))}
        timeout = httpx.Timeout(None, connect=15.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for cand in self._provider_candidates():
                sent = False
                async for chunk in self._openai_stream(client, cand["base"], cand.get("key", ""), payload):
                    sent = True
                    yield chunk
                if sent:
                    return
        for chunk in re.findall(r".{1,120}(?:\s+|$)", self._setup_message(mode), re.S):
            yield chunk

    async def generate_image(self, prompt: str, model: Optional[str] = None, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        return {
            "status": "ready",
            "prompt": prompt,
            "model": model or settings.DEFAULT_IMAGE_MODEL,
            "width": width,
            "height": height,
            "image_url": f"https://image.pollinations.ai/prompt/{httpx.QueryParams({'prompt': prompt, 'width': width, 'height': height})['prompt']}" if prompt else None,
        }

    async def generate_email(self, purpose: str, recipient: str, tone: str = "professional", details: str = "") -> str:
        messages = [{"role": "user", "content": f"Write an email.\nRecipient: {recipient}\nPurpose: {purpose}\nTone: {tone}\nDetails: {details}\nInclude a clear subject line and polished body."}]
        return await self.chat_completion(messages, mode="writer")

    async def create_document(self, doc_type: str, topic: str, requirements: str = "") -> str:
        messages = [{"role": "user", "content": f"Create a high-quality {doc_type}.\nTopic: {topic}\nRequirements: {requirements}\nUse clear headings, structured sections, and practical detail."}]
        return await self.chat_completion(messages, mode="writer")

    async def research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        messages = [{"role": "user", "content": f"Research request ({depth}).\nTopic: {query}\nProvide an elaborate, well-structured response with background, key findings, implications, limitations/uncertainty, and recommended next steps."}]
        content = await self.chat_completion(messages, mode="research")
        return {"query": query, "content": content, "sources": [], "depth": depth}


ai_service = AethrixAIService()

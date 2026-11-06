import json
import os
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.core.config import settings
from app.services.engine import capability_notice, deterministic_response, last_user_text


class AethrixAIService:
    """
    Owned AETHRIX orchestration.
    - Always available: owned API + deterministic engine (verified math, etc.).
    - For broad open-domain intelligence: connects to a SELF-HOSTED model endpoint
      controlled by the operator (Ollama / OpenAI-compatible gateway on your infra).
      No commercial AI assistant APIs are hardcoded.
    """

    SYSTEM_PROMPTS = {
        "assistant": (
            "You are AETHRIX, a highly intelligent assistant running on the user's own platform. "
            "Your priorities are correctness, logical reasoning, honesty, and usefulness. "
            "Understand intent, reason step by step, verify logic/math when possible, consider edge cases, and state uncertainty clearly. "
            "Give elaborate, structured answers (markdown headings/lists/tables/code blocks) when helpful. "
            "Never fabricate facts; if unsure, say what you know, what you assume, and how to verify."
        ),
        "coder": "You are AETHRIX Coder. Give correct, secure, maintainable solutions with explanations, edge cases, and verification steps.",
        "writer": "You are AETHRIX Writer. Produce clear, polished, audience-aware writing.",
        "research": "You are AETHRIX Research. Analyze carefully, separate facts from inference, note uncertainty, and give actionable conclusions.",
        "tutor": "You are AETHRIX Tutor. Teach step by step, adapt to level, use examples, and check understanding.",
        "planner": "You are AETHRIX Planner. Produce concrete plans with priorities, dependencies, risks, and next actions.",
    }

    def __init__(self):
        self.ollama_url = (settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")

    @property
    def default_chat_model(self) -> str:
        return settings.resolved_ai_model() or settings.DEFAULT_CHAT_MODEL or "llama3.1"

    def status(self) -> Dict[str, Any]:
        base = (settings.resolved_ai_base_url() or "").strip()
        return {
            "ready": True,
            "engine": "aethrix-owned",
            "commercial_api_dependency": False,
            "self_hosted_endpoint_configured": bool(base or self.ollama_url),
            "model": self.default_chat_model,
            "capabilities": {
                "verified_math": True,
                "chat_api": True,
                "streaming": True,
                "open_domain_requires_self_hosted_model": True,
            },
        }

    def has_provider_config(self) -> bool:
        return bool((settings.resolved_ai_base_url() or "").strip() or self.ollama_url)

    def available_models(self) -> List[Dict[str, Any]]:
        out = [{"id": "auto", "name": "AETHRIX Auto", "provider": "aethrix"}]
        m = self.default_chat_model
        if m and not any(x["id"] == m for x in out):
            out.append({"id": m, "name": m, "provider": "self-hosted"})
        for x in ["llama3.1", "qwen2.5:7b", "mistral", "gemma2:9b", "phi4", "deepseek-r1:8b"]:
            if not any(i["id"] == x for i in out):
                out.append({"id": x, "name": x, "provider": "self-hosted"})
        return out

    async def detect_ollama_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.ollama_url}/api/tags")
                if r.status_code == 200:
                    return [m.get("name") for m in (r.json() or {}).get("models", []) if m.get("name")]
        except Exception:
            pass
        return []

    def _normalize_messages(self, messages: List[Dict[str, str]], mode: str = "assistant", system: Optional[str] = None) -> List[Dict[str, str]]:
        sys = (system or "").strip() or self.SYSTEM_PROMPTS.get(mode, self.SYSTEM_PROMPTS["assistant"])
        cleaned = [{"role": "system", "content": sys}]
        for m in messages or []:
            if not isinstance(m, dict):
                continue
            role = str(m.get("role") or "user").lower()
            if role not in {"user", "assistant"}:
                continue
            content = str(m.get("content") or "").strip()
            if content:
                cleaned.append({"role": role, "content": content})
        return [cleaned[0]] + cleaned[-60:] if len(cleaned) > 61 else cleaned

    def _candidates(self):
        out = []
        base = (settings.resolved_ai_base_url() or "").rstrip("/")
        key = settings.resolved_ai_api_key() or ""
        if base:
            out.append({"base": base, "key": key, "kind": "openai"})
            if not base.endswith("/v1"):
                out.append({"base": base + "/v1", "key": key, "kind": "openai"})
        # Self-hosted Ollama on operator-controlled host
        out.append({"base": self.ollama_url, "key": "", "kind": "ollama"})
        out.append({"base": self.ollama_url + "/v1", "key": "", "kind": "openai"})
        # de-dupe
        seen = set(); res = []
        for c in out:
            k = (c["base"], c["kind"])
            if k not in seen:
                seen.add(k); res.append(c)
        return res

    async def _try_generate(self, client: httpx.AsyncClient, cand: Dict[str, str], payload: Dict[str, Any]) -> Optional[str]:
        headers = {"Content-Type": "application/json"}
        if cand.get("key"):
            headers["Authorization"] = f"Bearer {cand['key']}"
        attempts = []
        if cand["kind"] == "openai":
            attempts = [("/chat/completions", payload), ("/v1/chat/completions", payload)]
        else:
            attempts = [
                ("/api/chat", {"model": payload["model"], "messages": payload["messages"], "stream": False, "options": {"temperature": payload.get("temperature", 0.4), "num_predict": payload.get("max_tokens", 2048)}}),
                ("/chat/completions", payload),
            ]
        for path, body in attempts:
            url = cand["base"].rstrip("/") + path
            url = url.replace("/v1/v1/", "/v1/")
            try:
                r = await client.post(url, json=body, headers=headers)
                if r.status_code != 200:
                    continue
                data = r.json() if r.content else {}
                text = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content")
                if not text:
                    text = ((data.get("message") or {}).get("content"))
                if isinstance(text, str) and text.strip():
                    return text.strip()
            except Exception:
                continue
        return None

    async def _stream_generate(self, client: httpx.AsyncClient, cand: Dict[str, str], payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        headers = {"Content-Type": "application/json"}
        if cand.get("key"):
            headers["Authorization"] = f"Bearer {cand['key']}"
        attempts = []
        if cand["kind"] == "openai":
            attempts = [("/chat/completions", {**payload, "stream": True}), ("/v1/chat/completions", {**payload, "stream": True})]
        else:
            attempts = [("/api/chat", {"model": payload["model"], "messages": payload["messages"], "stream": True, "options": {"temperature": payload.get("temperature", 0.4), "num_predict": payload.get("max_tokens", 2048)}})]
        for path, body in attempts:
            url = cand["base"].rstrip("/") + path
            url = url.replace("/v1/v1/", "/v1/")
            try:
                async with client.stream("POST", url, json=body, headers=headers) as r:
                    if r.status_code != 200:
                        continue
                    sent = False
                    async for line in r.aiter_lines():
                        if not line:
                            continue
                        raw = line[5:].strip() if line.startswith("data:") else line
                        if raw == "[DONE]":
                            if sent: return
                            break
                        try:
                            obj = json.loads(raw)
                        except Exception:
                            continue
                        delta = (((obj.get("choices") or [{}])[0]).get("delta") or {}).get("content") or ((obj.get("message") or {}).get("content"))
                        if isinstance(delta, str) and delta:
                            sent = True
                            yield delta
                    if sent:
                        return
            except Exception:
                continue
        return

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.4, max_tokens: int = 4096, mode: str = "assistant", system: Optional[str] = None) -> str:
        det = deterministic_response(messages, mode)
        if det is not None:
            return det
        norm = self._normalize_messages(messages, mode=mode, system=system)
        use_model = (model or self.default_chat_model or "llama3.1").strip()
        if use_model == "auto":
            use_model = self.default_chat_model or "llama3.1"
        payload = {"model": use_model, "messages": norm, "temperature": max(0.0, min(float(temperature or 0.4), 2.0)), "max_tokens": max(256, min(int(max_tokens or 4096), 8192))}
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=8.0)) as client:
            for cand in self._candidates():
                text = await self._try_generate(client, cand, payload)
                if text:
                    return text
        return capability_notice() + "\n\n**Your message:** " + last_user_text(messages)[:1500]

    async def stream_chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.4, max_tokens: int = 4096, mode: str = "assistant", system: Optional[str] = None) -> AsyncGenerator[str, None]:
        det = deterministic_response(messages, mode)
        if det is not None:
            for c in re.findall(r".{1,80}(?:\s+|$)", det, re.S):
                yield c
            return
        norm = self._normalize_messages(messages, mode=mode, system=system)
        use_model = (model or self.default_chat_model or "llama3.1").strip()
        if use_model == "auto":
            use_model = self.default_chat_model or "llama3.1"
        payload = {"model": use_model, "messages": norm, "temperature": max(0.0, min(float(temperature or 0.4), 2.0)), "max_tokens": max(256, min(int(max_tokens or 4096), 8192))}
        async with httpx.AsyncClient(timeout=httpx.Timeout(None, connect=8.0)) as client:
            for cand in self._candidates():
                sent = False
                async for chunk in self._stream_generate(client, cand, payload):
                    sent = True
                    yield chunk
                if sent:
                    return
        msg = capability_notice() + "\n\n**Your message:** " + last_user_text(messages)[:1500]
        for c in re.findall(r".{1,80}(?:\s+|$)", msg, re.S):
            yield c

    async def generate_email(self, purpose: str, recipient: str, tone: str = "professional", details: str = "") -> str:
        return await self.chat_completion([{"role": "user", "content": f"Write an email. Recipient: {recipient}. Purpose: {purpose}. Tone: {tone}. Details: {details}. Include subject and body."}], mode="writer")

    async def create_document(self, doc_type: str, topic: str, requirements: str = "") -> str:
        return await self.chat_completion([{"role": "user", "content": f"Create a high-quality {doc_type} about: {topic}. Requirements: {requirements}."}], mode="writer")

    async def research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        content = await self.chat_completion([{"role": "user", "content": f"Research ({depth}): {query}. Provide background, key points, logical analysis, uncertainty, and next steps. Be accurate; do not invent facts."}], mode="research")
        return {"query": query, "content": content, "sources": [], "depth": depth, "engine": "aethrix"}

    async def generate_image(self, prompt: str, model: Optional[str] = None, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        # No external AI API dependency. Connect your own self-hosted image backend if desired.
        return {"status": "not_configured", "prompt": prompt, "model": model or "self-hosted", "width": width, "height": height, "message": "Image generation requires your own self-hosted image model/backend. The AETHRIX API is ready to integrate it."}


ai_service = AethrixAIService()

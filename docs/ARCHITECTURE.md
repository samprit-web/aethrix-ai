# AETHRIX AI Architecture (Owned)

## Principle
AETHRIX is built to be **owned by you**: your UI, your API, your data model, your orchestration, and your deployment. The code in this repository does **not** require commercial AI assistant APIs.

## Components
- **Frontend (Next.js)**: ChatGPT/Gemini-style UI, streaming chat, tools pages. Uses your backend API (`/api/v1`).
- **Backend API (FastAPI)**: Auth, conversations, chat streaming, tools, and the AETHRIX engine endpoints. This is your own API surface.
- **AETHRIX Engine (`backend/app/services/engine.py`)**: Deterministic, owned capabilities (verified math, intent routing, structured responses). Safe expression evaluation runs locally.
- **Model Orchestration (`backend/app/services/ai_service.py`)**: Routes chat to a **self-hosted open-weights model** that you run (Ollama/llama.cpp/vLLM/TGI/OpenAI-compatible gateway on your infrastructure) and falls back to the deterministic engine when no model is available.

## “No dependency / answers everything” reality
To answer arbitrary questions **correctly and logically across all domains** at the level of large assistants, you need a capable language model. AETHRIX is designed so that model can be:
- **open-weights** and **self-hosted** on hardware you control,
- accessed only through **your own** endpoint (`AI_BASE_URL` / `OLLAMA_BASE_URL`),
- without sending traffic to commercial AI assistant APIs.

AETHRIX will **not fabricate** open-domain answers when no capable model is connected; it will use deterministic results where verifiable (e.g., math) and provide explicit self-hosting setup guidance.

## Self-hosted setup (owned inference)
1. Run an inference server you control (recommended: Ollama).
2. Pull an open-weights model you choose/have rights to run (example): `ollama pull llama3.1`.
3. Configure backend env vars:
   - `OLLAMA_BASE_URL=http://<your-host>:11434`
   - `DEFAULT_CHAT_MODEL=<model>`
   - or `AI_BASE_URL=http://<your-gateway>/v1` + `AI_MODEL=<model>` (+ `AI_API_KEY` only if your own gateway requires it)
4. Deploy the backend where it can reach that host. Vercel serverless can host the API layer, but **large models should run on your own compute** (VPS/GPU server/Docker host) and be exposed securely to the backend.

## Verification
- `GET /api/v1/chat/status` — engine/model config status.
- `GET /api/v1/engine/status` — owned engine status.
- `POST /api/v1/engine/calc` — deterministic verified calculation.

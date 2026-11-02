# AETHRIX AI

A completely original, independent, worldwide public AI platform. Free-to-use alternative to ChatGPT, Gemini and Grok with AI chat, original image generation, email drafting, meeting scheduling, document creation, research and productivity tools.

## Vision
- **Free Forever**: No advertisements, ever. Core features remain free for everyone worldwide.
- **Independent**: Original architecture, no dependency on other commercial AI assistant APIs.
- **Open & Self-Hostable**: Built on open-source models that can run independently.
- **Privacy-Focused**: Secure user accounts with privacy-first design.
- **Sustainable**: Funded through optional premium services, donations and subscriptions only.

## Features
- **AI Chat** - Conversational AI with multiple open-source models
- **Original Image Generation** - Create images using open-source diffusion models
- **Email Drafting** - AI-powered email composition and refinement
- **Meeting Scheduling** - Smart scheduling assistant with calendar integration
- **Document Creation** - Generate documents, reports, and presentations
- **Research Tools** - Deep research with web search capabilities
- **Productivity Tools** - Summaries, translations, code assistance, and more

## Tech Stack
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI (Python) with original API architecture
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: Custom JWT-based auth with secure sessions
- **AI Models**: Ollama (self-hostable), HuggingFace Inference, or custom deployments
- **Storage**: S3-compatible storage (Cloudflare R2, MinIO)
- **Cache**: Redis (optional)

## Architecture
AETHRIX uses a modular, microservice-inspired architecture that can scale from single-server deployment to distributed systems. All AI inference goes through our own model orchestration layer - no third-party commercial AI APIs.

## Getting Started
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment instructions.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details.

## License
Open source - see LICENSE file for details.

## Domain
Designed for deployment on a unique professional domain (e.g., aethrix.ai)

# AETHRIX AI Architecture

## Overview
AETHRIX AI is built with a completely original, modular architecture designed for independence and scalability. No dependencies on commercial AI assistant APIs.

## System Architecture

### Frontend (Next.js 15)
- **Framework**: Next.js with App Router
- **Styling**: Tailwind CSS with custom futuristic theme
- **UI Components**: Custom components with cyberpunk/aethrix aesthetic
- **State Management**: React hooks and context
- **Authentication**: JWT token-based auth

### Backend (FastAPI)
- **Framework**: FastAPI for high-performance async API
- **Architecture**: RESTful API with versioning (/api/v1)
- **Authentication**: OAuth2 with JWT tokens
- **Validation**: Pydantic schemas
- **Database ORM**: SQLAlchemy

### Database Layer
- **Primary DB**: PostgreSQL for relational data
- **Models**: Users, Conversations, Messages, Images, Documents, Email Drafts
- **Migrations**: Alembic for schema management

### AI Orchestration Layer
- **Service**: Custom AethrixAIService
- **Model Backend**: Ollama (primary), supports any OpenAI-compatible API
- **Models**: LLaMA, Mistral, Gemma, Stable Diffusion (all open-source)
- **No Third-Party APIs**: Completely self-hosted capable

### Storage
- **File Uploads**: Local filesystem or S3-compatible (Cloudflare R2, MinIO)
- **Images**: Generated images stored with metadata

## Security
- **Authentication**: Secure password hashing with bcrypt
- **Tokens**: JWT with configurable expiration
- **CORS**: Configured for specific origins
- **Rate Limiting**: Built-in rate limiting
- **Input Validation**: All inputs validated with Pydantic

## Deployment Options
1. **Single Server**: Docker Compose with all services
2. **Distributed**: Separate frontend, backend, database, AI models
3. **Self-Hosted**: Run entirely on own infrastructure
4. **Cloud**: Deploy to any cloud provider

## Independence Principles
- **No External AI Dependencies**: All inference through self-hosted/open models
- **Original Codebase**: Built from scratch, no forks of commercial products
- **Open Source Models**: Only use models with open licenses
- **Self-Sufficient**: Can operate without internet to third-party AI services
- **Data Sovereignty**: All data stays under platform control

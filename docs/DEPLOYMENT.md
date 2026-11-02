# AETHRIX AI Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Domain name (for production)
- SSL certificate
- Server with adequate resources (minimum 8GB RAM for AI models)

## Quick Start with Docker Compose

1. Clone the repository
2. Copy environment variables
3. Start services
4. Configure AI models
5. Access the platform

## Environment Configuration

Create `.env` files for backend and frontend.

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://aethrix:password@db:5432/aethrix
REDIS_HOST=redis
OLLAMA_BASE_URL=http://ollama:11434
DOMAIN=aethrix.ai
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://api.aethrix.ai
```

## AI Models Setup

### Using Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull open-source models
ollama pull llama-3.1-8b
ollama pull mistral
ollama pull gemma2:9b
ollama pull llama-3.2-vision  # for vision capabilities
```

### Using Stable Diffusion
Models will be downloaded automatically or can be pre-downloaded to the models directory.

## Production Deployment

### Domain Setup
Point your domain to your server IP:
- `aethrix.ai` -> Frontend
- `api.aethrix.ai` -> Backend API

### SSL/TLS
Use Let's Encrypt with Certbot or Cloudflare Tunnel for HTTPS.

### Security Considerations
- Change all default passwords
- Use strong SECRET_KEY
- Enable firewall
- Regular updates
- Monitor resources

## Zero-Budget Options
- **Free Hosting**: Oracle Cloud Free Tier, Railway, Render (free tiers)
- **Domain**: Many registrars offer affordable domains, or use subdomains
- **Storage**: Cloudflare R2 has free tier
- **CDN**: Cloudflare free tier
- **AI Models**: Self-host on free tier instances or use local models

## Monitoring
- Health check endpoints: `/health` and `/api/v1/health`
- Logs via Docker
- Resource monitoring recommended

#!/bin/bash

echo "🚀 Setting up AETHRIX AI..."

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "📦 Building and starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🤖 Pulling AI models..."
docker exec aethrix-ollama-1 ollama pull llama-3.1-8b 2>/dev/null || docker-compose exec ollama ollama pull llama-3.1-8b

echo "✅ AETHRIX AI setup complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# AETHRIX - Complete Original AI System

## Summary
AETHRIX is a fully independent, original AI model system built from scratch with:
- Custom transformer architecture
- Original tokenizer (BPE)
- Complete training pipeline
- Inference engine with memory and reasoning
- REST API server
- No third-party AI dependencies

## Quick Start

### Train Model
```bash
python aethrix/scripts/train_aethrix.py
```

### Run Inference Server
```bash
python -m aethrix.api.server
```

### Use in Code
```python
from aethrix.inference.engine import AethrixInference
engine = AethrixInference()
response = engine.chat("Hello, who are you?")
print(response)
```

## Features
- Intelligent conversation
- Advanced reasoning (step by step)
- Code generation and assistance
- Mathematical problem solving
- Research capabilities
- Long-term memory
- Tool integration ready
- Multi-language support

## Architecture Highlights
- Grouped Query Attention for efficiency
- Rotary Positional Embeddings
- RMSNorm normalization
- SwiGLU activation
- Weight tying
- Custom training loop

All components developed independently. No reliance on external AI models or APIs.

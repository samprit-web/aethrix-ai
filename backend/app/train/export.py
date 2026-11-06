"""Export a fine-tuned model to Ollama-compatible format."""

import json
from pathlib import Path
from typing import Optional

from app.train.config import TrainingConfig


def export_to_ollama(
    model_dir: str,
    modelfile_path: Optional[str] = None,
    model_name: str = "aethrix-ai",
    base_model: str = "llama-3.1-8b",
) -> str:
    """Generate an Ollama Modelfile for the fine-tuned model.

    The fine-tuned weights (PyTorch/safetensors) must first be converted to
    GGUF format using llama.cpp (see docs/TRAINING.md). This function writes the
    Modelfile that tells Ollama how to serve the converted model.
    """
    model_path = Path(model_dir)
    if not model_path.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    out_path = Path(modelfile_path or f"{model_dir}/Modelfile")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Locate a GGUF file if present, otherwise reference the base model name.
    gguf_files = list(model_path.glob("*.gguf"))
    gguf_ref = gguf_files[0].name if gguf_files else base_model

    modelfile = f"""# AETHRIX AI fine-tuned model
FROM ./{gguf_ref}

# System prompt defining the assistant identity
SYSTEM \"\"\"You are AETHRIX AI, an independent, open-source AI assistant. You are helpful, honest, and harmless. You do not rely on third-party commercial AI APIs.\"\"\"

# Generation parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 2048
"""

    out_path.write_text(modelfile, encoding="utf-8")
    return str(out_path)

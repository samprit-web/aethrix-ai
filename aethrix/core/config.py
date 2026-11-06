from dataclasses import dataclass
from typing import Optional
import torch

@dataclass
class AethrixConfig:
    """Configuration for AETHRIX model architecture"""
    # Model architecture
    vocab_size: int = 50000
    hidden_size: int = 4096
    num_hidden_layers: int = 32
    num_attention_heads: int = 32
    num_key_value_heads: int = 8
    intermediate_size: int = 11008
    hidden_act: str = "silu"
    max_position_embeddings: int = 4096
    rms_norm_eps: float = 1e-6
    rope_theta: float = 10000.0
    
    # Training
    batch_size: int = 4
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 2000
    max_steps: int = 100000
    gradient_accumulation_steps: int = 8
    
    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: str = "float16" if torch.cuda.is_available() else "float32"
    
    # Model info
    model_name: str = "AETHRIX-7B"
    version: str = "1.0.0-alpha"
    is_original: bool = True
    no_external_deps: bool = True

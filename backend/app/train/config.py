"""Training configuration for fine-tuning the AETHRIX AI model."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrainingConfig:
    """Hyperparameters and paths for model fine-tuning."""

    # Model
    base_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    output_dir: str = "./models/fine-tuned"
    model_name: str = "aethrix-ai"

    # Data
    dataset_path: str = "./data/training.jsonl"
    dataset_text_field: str = "text"
    train_split: float = 0.9

    # Training hyperparameters
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 1
    learning_rate: float = 2e-4
    max_seq_length: int = 2048
    warmup_steps: int = 100
    weight_decay: float = 0.01
    lr_scheduler_type: str = "cosine"
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 500
    save_total_limit: int = 2
    seed: int = 42

    # LoRA (PEFT) configuration
    use_peft: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: Optional[list] = None

    # Quantization
    load_in_4bit: bool = False
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

    # Ollama export
    ollama_modelfile_path: str = "./models/fine-tuned/Modelfile"
    ollama_model_name: str = "aethrix-ai"

    def __post_init__(self):
        if self.lora_target_modules is None:
            self.lora_target_modules = ["q_proj", "v_proj"]

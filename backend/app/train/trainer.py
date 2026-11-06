"""Fine-tuning trainer for the AETHRIX AI model.

Uses HuggingFace transformers + PEFT (LoRA) + TRL SFTTrainer to train on
open-source base models, then saves adapters/merged weights for Ollama export.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from app.train.config import TrainingConfig
from app.train.dataset import TrainingDataset

logger = logging.getLogger(__name__)


class AethrixTrainer:
    """Runs supervised fine-tuning of the AETHRIX AI chat model."""

    def __init__(self, config: Optional[TrainingConfig] = None):
        self.config = config or TrainingConfig()
        self.model = None
        self.tokenizer = None
        self.trainer = None

    def _check_deps(self) -> None:
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
            import peft  # noqa: F401
            import trl  # noqa: F401
            import datasets  # noqa: F401
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "Training dependencies are not installed. "
                "Run: pip install -r backend/requirements.txt"
            ) from exc

    def train(self) -> Dict[str, Any]:
        """Execute the full fine-tuning run and return a summary dict."""
        self._check_deps()

        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        from datasets import Dataset

        cfg = self.config
        Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)

        # Tokenizer
        tokenizer = AutoTokenizer.from_pretrained(cfg.base_model, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Model (optional 4-bit quantization)
        model_kwargs: Dict[str, Any] = {"trust_remote_code": True}
        if cfg.load_in_4bit:
            try:
                from transformers import BitsAndBytesConfig
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=getattr(torch, cfg.bnb_4bit_compute_dtype),
                    bnb_4bit_quant_type=cfg.bnb_4bit_quant_type,
                    bnb_4bit_use_double_quant=cfg.bnb_4bit_use_double_quant,
                )
                model_kwargs["device_map"] = {"": 0}
            except ImportError as exc:
                raise RuntimeError("4-bit quantization requires bitsandbytes") from exc

        model = AutoModelForCausalLM.from_pretrained(cfg.base_model, **model_kwargs)

        if cfg.load_in_4bit:
            model = prepare_model_for_kbit_training(model)

        # PEFT / LoRA
        if cfg.use_peft:
            lora_config = LoraConfig(
                r=cfg.lora_r,
                lora_alpha=cfg.lora_alpha,
                lora_dropout=cfg.lora_dropout,
                target_modules=cfg.lora_target_modules,
                bias="none",
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()

        # Dataset (raw text; SFTTrainer handles tokenization via dataset_text_field)
        ds = TrainingDataset(cfg)
        examples = ds.load()
        if not examples:
            sample_path = ds.save_sample()
            raise RuntimeError(
                f"No training examples found in {cfg.dataset_path}. "
                f"A sample dataset was written to {sample_path}. "
                "Fill it with your data and re-run training."
            )
        hf_dataset = Dataset.from_list(examples)

        # Split train/eval
        split = hf_dataset.train_test_split(test_size=1.0 - cfg.train_split, seed=cfg.seed)
        train_ds = split["train"]
        eval_ds = split["test"]

        # Training arguments
        training_args = TrainingArguments(
            output_dir=cfg.output_dir,
            per_device_train_batch_size=cfg.batch_size,
            per_device_eval_batch_size=cfg.batch_size,
            gradient_accumulation_steps=cfg.gradient_accumulation_steps,
            learning_rate=cfg.learning_rate,
            weight_decay=cfg.weight_decay,
            num_train_epochs=cfg.epochs,
            warmup_steps=cfg.warmup_steps,
            lr_scheduler_type=cfg.lr_scheduler_type,
            logging_steps=cfg.logging_steps,
            save_steps=cfg.save_steps,
            eval_steps=cfg.eval_steps,
            save_total_limit=cfg.save_total_limit,
            seed=cfg.seed,
            fp16=not cfg.load_in_4bit and torch.cuda.is_available(),
            bf16=cfg.load_in_4bit and torch.cuda.is_available(),
            report_to="none",
            load_best_model_at_end=True if len(eval_ds) > 0 else False,
        )

        # SFT trainer (tokenizes the "text" field internally)
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=eval_ds if len(eval_ds) > 0 else None,
            tokenizer=tokenizer,
            dataset_text_field="text",
            max_seq_length=cfg.max_seq_length,
        )

        self.model = model
        self.tokenizer = tokenizer
        self.trainer = trainer

        train_result = trainer.train()
        trainer.save_model(cfg.output_dir)
        tokenizer.save_pretrained(cfg.output_dir)

        # Save training metrics
        metrics = {
            "train_runtime": train_result.metrics.get("train_runtime"),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second"),
            "train_loss": train_result.metrics.get("train_loss"),
        }
        if len(eval_ds) > 0:
            eval_result = trainer.evaluate()
            metrics["eval_loss"] = eval_result.get("eval_loss")

        return {
            "status": "completed",
            "output_dir": cfg.output_dir,
            "base_model": cfg.base_model,
            "metrics": metrics,
        }

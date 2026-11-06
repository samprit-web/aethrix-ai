#!/usr/bin/env python3
"""CLI entrypoint to fine-tune the AETHRIX AI model.

Usage:
    python scripts/train.py --dataset ./data/training.jsonl --epochs 3 --output ./models/fine-tuned
    python scripts/train.py --sample   # write a sample dataset and exit
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root or backend dir
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.train.config import TrainingConfig  # noqa: E402
from app.train.dataset import TrainingDataset  # noqa: E402
from app.train.trainer import AethrixTrainer  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fine-tune the AETHRIX AI model")
    parser.add_argument("--dataset", default="./data/training.jsonl", help="Path to JSONL training dataset")
    parser.add_argument("--output", default="./models/fine-tuned", help="Output directory for the fine-tuned model")
    parser.add_argument("--base-model", default="TinyLlama/TinyLlama-1.1B-Chat-v1.0", help="Base HuggingFace model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Per-device train batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--max-seq-length", type=int, default=2048, help="Max sequence length")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--no-peft", action="store_true", help="Disable PEFT/LoRA (full fine-tune)")
    parser.add_argument("--load-in-4bit", action="store_true", help="Load base model in 4-bit (requires GPU + bitsandbytes)")
    parser.add_argument("--sample", action="store_true", help="Write a sample dataset and exit")
    args = parser.parse_args()

    if args.sample:
        cfg = TrainingConfig(dataset_path=args.dataset, output_dir=args.output)
        ds = TrainingDataset(cfg)
        path = ds.save_sample()
        print(f"Sample dataset written to {path}")
        return 0

    cfg = TrainingConfig(
        base_model=args.base_model,
        output_dir=args.output,
        dataset_path=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_seq_length=args.max_seq_length,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        use_peft=not args.no_peft,
        load_in_4bit=args.load_in_4bit,
    )

    trainer = AethrixTrainer(cfg)
    result = trainer.train()
    print("Training complete.")
    print(f"  Output dir: {result['output_dir']}")
    print(f"  Base model: {result['base_model']}")
    print(f"  Train loss: {result['metrics'].get('train_loss')}")
    if result["metrics"].get("eval_loss") is not None:
        print(f"  Eval loss: {result['metrics']['eval_loss']}")
    if result.get("ollama_modelfile"):
        print(f"  Ollama Modelfile: {result['ollama_modelfile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

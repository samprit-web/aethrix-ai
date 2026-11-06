"""Dataset loading and formatting for AETHRIX AI fine-tuning."""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.train.config import TrainingConfig


class TrainingDataset:
    """Loads and formats training data into a chat-style text format."""

    def __init__(self, config: TrainingConfig):
        self.config = config

    def load(self) -> List[Dict[str, Any]]:
        """Load training examples from a JSONL file.

        Supported per-line shapes:
          - {"text": "..."}
          - {"instruction": "...", "output": "..."}
          - {"prompt": "...", "completion": "..."}
          - {"conversations": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
        """
        path = Path(self.config.dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Training dataset not found: {path}")

        examples: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                text = self._format_example(obj)
                if text:
                    examples.append({"text": text})
        return examples

    def _format_example(self, obj: Dict[str, Any]) -> str:
        if "text" in obj and obj["text"]:
            return str(obj["text"])

        if "instruction" in obj and "output" in obj:
            instruction = str(obj["instruction"]).strip()
            output = str(obj["output"]).strip()
            inp = str(obj.get("input", "")).strip()
            if inp:
                return f"### User: {instruction}\nInput: {inp}\n### Assistant: {output}"
            return f"### User: {instruction}\n### Assistant: {output}"

        if "prompt" in obj and "completion" in obj:
            return f"### User: {obj['prompt'].strip()}\n### Assistant: {obj['completion'].strip()}"

        if "conversations" in obj:
            parts: List[str] = []
            for turn in obj["conversations"]:
                role = str(turn.get("role", "user")).strip()
                content = str(turn.get("content", "")).strip()
                if role == "assistant":
                    parts.append(f"### Assistant: {content}")
                else:
                    parts.append(f"### User: {content}")
            return "\n".join(parts)

        return ""

    def save_sample(self, path: Optional[str] = None) -> str:
        """Write a small sample dataset so users can see the expected format."""
        target = Path(path or self.config.dataset_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        samples = [
            {"text": "### User: What is AETHRIX AI?\n### Assistant: AETHRIX AI is an independent, open-source AI platform built for free, privacy-focused conversational AI."},
            {"text": "### User: Draft a professional email to a client about a project delay.\n### Assistant: Subject: Project Update\n\nDear Client,\n\nI wanted to inform you that there will be a slight delay in the project delivery. We are working to resolve this quickly and will keep you updated.\n\nBest regards,\nAETHRIX AI"},
            {"text": "### User: Summarize the key points of a meeting.\n### Assistant: Key points:\n- Project timeline reviewed\n- Deliverables assigned\n- Next meeting scheduled for Friday"},
        ]
        with target.open("w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        return str(target)

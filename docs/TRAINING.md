# AETHRIX AI — Model Training

AETHRIX AI originally only performed **inference** through Ollama (pre-trained open-source models). This guide adds the ability to **fine-tune** the model on your own data so the existing `AethrixAIService` serves a customized assistant.

## What was added

| Component | Path | Purpose |
|-----------|------|---------|
| Dependencies | `backend/requirements.txt` | torch, transformers, accelerate, datasets, peft, bitsandbytes, trl |
| Config | `backend/app/train/config.py` | `TrainingConfig` dataclass (model, data, hyperparams, LoRA) |
| Dataset | `backend/app/train/dataset.py` | JSONL loader supporting `text`, `instruction`/`output`, `prompt`/`completion`, `conversations` |
| Trainer | `backend/app/train/trainer.py` | `AethrixTrainer` using PEFT/LoRA + TRL `SFTTrainer` |
| Export | `backend/app/train/export.py` | Writes an Ollama `Modelfile` from fine-tuned weights |
| Service | `backend/app/services/training_service.py` | `AethrixTrainingService` — async job tracking |
| API | `backend/app/api/v1/training.py` | `POST /training/start`, `GET /training/jobs`, `GET /training/jobs/{id}` |
| CLI | `scripts/train.py` | Command-line fine-tuning entrypoint |

## Dataset format

Create a JSONL file (one JSON object per line). Supported shapes:

```jsonl
{"text": "### User: What is AETHRIX AI?\n### Assistant: AETHRIX AI is an independent open-source AI platform."}
{"instruction": "Draft a professional email", "output": "Subject: ...\n\nDear ...", "input": "to a client about a delay"}
{"prompt": "Summarize this meeting", "completion": "Key points:\n- ..."}
{"conversations": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello! How can I help?"}]}
```

All examples are normalized to `### User: ...\n### Assistant: ...` training text.

Generate a sample dataset:

```bash
python scripts/train.py --sample --dataset ./data/training.jsonl
```

Then edit `./data/training.jsonl` with your own examples.

## Quick start (CLI)

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Prepare a dataset
python scripts/train.py --sample --dataset ./data/training.jsonl
# edit ./data/training.jsonl with your data

# 3. Fine-tune
python scripts/train.py \
  --dataset ./data/training.jsonl \
  --output ./models/fine-tuned \
  --epochs 3 \
  --batch-size 4 \
  --learning-rate 2e-4
```

Output: `./models/fine-tuned/` (adapter + tokenizer) and `./models/fine-tuned/Modelfile`.

## Quick start (API)

```bash
# Start a job
curl -X POST http://localhost:8000/training/start \
  -H "Content-Type: application/json" \
  -d '{"epochs":3,"batch_size":4,"dataset_path":"./data/training.jsonl"}'

# Check status
curl http://localhost:8000/training/jobs/<job_id>
curl http://localhost:8000/training/jobs
```

Jobs run in the background via FastAPI `BackgroundTasks`.

## Using the fine-tuned model with Ollama

The trainer saves PyTorch/safetensors weights. Ollama needs a **GGUF** file. Convert with llama.cpp:

```bash
# Clone llama.cpp and convert (example)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
python convert-hf-to-gguf.py ../models/fine-tuned --outtype f16
# produces a .gguf file in ../models/fine-tuned/
```

Then create/import in Ollama using the generated `Modelfile`:

```bash
ollama create aethrix-ai -f ./models/fine-tuned/Modelfile
ollama run aethrix-ai "Hello"
```

Point the backend at it via `backend/app/core/config.py`:

```python
DEFAULT_CHAT_MODEL: str = "aethrix-ai"   # or your Ollama model name
OLLAMA_BASE_URL: str = "http://localhost:11434"
```

The existing `AethrixAIService.chat_completion` then serves the fine-tuned model automatically.

## Hardware

- **CPU-only**: works for small models (e.g. TinyLlama 1.1B), slow.
- **GPU (CUDA)**: strongly recommended. Set `load_in_4bit=true` to reduce VRAM.
- 4-bit quantization requires `bitsandbytes` + a CUDA-capable GPU.

Docker Compose (`docker-compose.yml`) already passes GPUs to the `ollama` service; the `backend` image builds with `gcc`/`g++` for native wheels.

## Configuration reference (`TrainingConfig`)

| Field | Default | Description |
|-------|---------|-------------|
| `base_model` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | HuggingFace causal LM to fine-tune |
| `output_dir` | `./models/fine-tuned` | Where adapters/tokenizer are saved |
| `dataset_path` | `./data/training.jsonl` | Input JSONL training data |
| `train_split` | `0.9` | Train/eval split |
| `epochs` | `3` | Training epochs |
| `batch_size` | `4` | Per-device train batch size |
| `learning_rate` | `2e-4` | Learning rate |
| `max_seq_length` | `2048` | Max sequence length |
| `use_peft` | `True` | Enable LoRA (parameter-efficient) |
| `lora_r` | `16` | LoRA rank |
| `lora_alpha` | `32` | LoRA alpha |
| `load_in_4bit` | `False` | 4-bit load (GPU only) |
| `ollama_modelfile_path` | `./models/fine-tuned/Modelfile` | Exported Modelfile path |
| `ollama_model_name` | `aethrix-ai` | Name for the Ollama model |

## Files created by training

```
models/fine-tuned/
├── adapter_config.json      # PEFT/LoRA config
├── adapter_model.safetensors # LoRA weights
├── tokenizer.json
├── tokenizer_config.json
├── special_tokens_map.json
├── Modelfile                # Ollama serving file (after export)
└── *.gguf                   # converted GGUF (manual via llama.cpp)
```

## Notes

- LoRA adapters must be **merged** with the base model before GGUF conversion if you want a single-file model. `trainer.save_model()` saves adapters; use `model.merge_and_unload()` + `save_pretrained()` to merge.
- Ollama does not load raw PyTorch/LoRA directly — GGUF conversion via llama.cpp is required for the `Modelfile` to work.

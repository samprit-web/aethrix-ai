"""Training service layer for AETHRIX AI.

Coordinates fine-tuning runs, tracks job state, and exposes results to the API.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.train.config import TrainingConfig
from app.train.trainer import AethrixTrainer
from app.train.export import export_to_ollama

logger = logging.getLogger(__name__)


@dataclass
class TrainingJob:
    id: str
    status: str = "pending"  # pending | running | completed | failed
    config: Optional[TrainingConfig] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    progress: float = 0.0


class AethrixTrainingService:
    """Manages asynchronous training jobs."""

    def __init__(self):
        self.jobs: Dict[str, TrainingJob] = {}
        self._trainer: Optional[AethrixTrainer] = None

    def create_job(self, config: TrainingConfig) -> TrainingJob:
        import uuid

        job_id = f"train-{uuid.uuid4().hex[:8]}"
        job = TrainingJob(id=job_id, status="pending", config=config)
        self.jobs[job_id] = job
        logger.info("Created training job %s", job_id)
        return job

    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> list:
        return sorted(self.jobs.values(), key=lambda j: (j.started_at or 0), reverse=True)

    def run_job(self, job_id: str) -> Dict[str, Any]:
        """Run a training job (blocking; intended for a background thread)."""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Training job not found: {job_id}")

        job.status = "running"
        job.started_at = time.time()
        job.progress = 0.0

        try:
            cfg = job.config or TrainingConfig()
            self._trainer = AethrixTrainer(cfg)
            result = self._trainer.train()
            job.status = "completed"
            job.result = result
            job.progress = 1.0

            # Optionally export to Ollama Modelfile
            try:
                modelfile_path = export_to_ollama(
                    model_dir=cfg.output_dir,
                    modelfile_path=cfg.ollama_modelfile_path,
                    model_name=cfg.ollama_model_name,
                    base_model=cfg.base_model,
                )
                if result is None:
                    result = {}
                result["ollama_modelfile"] = modelfile_path
            except Exception as exc:  # export is non-fatal
                logger.warning("Ollama export skipped for job %s: %s", job_id, exc)

            job.finished_at = time.time()
            return result
        except Exception as exc:  # pragma: no cover - training failures
            logger.exception("Training job %s failed", job_id)
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = time.time()
            raise
        finally:
            self._trainer = None


training_service = AethrixTrainingService()

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.training_service import training_service
from app.train.config import TrainingConfig

router = APIRouter()


class TrainingStartRequest(BaseModel):
    base_model: Optional[str] = None
    dataset_path: Optional[str] = None
    output_dir: Optional[str] = None
    epochs: Optional[int] = None
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None
    max_seq_length: Optional[int] = None
    lora_r: Optional[int] = None
    lora_alpha: Optional[int] = None
    use_peft: Optional[bool] = None
    load_in_4bit: Optional[bool] = None


class TrainingStartResponse(BaseModel):
    job_id: str
    status: str


class TrainingJobResponse(BaseModel):
    id: str
    status: str
    progress: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@router.post("/start", response_model=TrainingStartResponse, tags=["training"])
def start_training(request: TrainingStartRequest, background_tasks: BackgroundTasks):
    """Start a model fine-tuning job in the background."""
    cfg = TrainingConfig()
    if request.base_model is not None:
        cfg.base_model = request.base_model
    if request.dataset_path is not None:
        cfg.dataset_path = request.dataset_path
    if request.output_dir is not None:
        cfg.output_dir = request.output_dir
    if request.epochs is not None:
        cfg.epochs = request.epochs
    if request.batch_size is not None:
        cfg.batch_size = request.batch_size
    if request.learning_rate is not None:
        cfg.learning_rate = request.learning_rate
    if request.max_seq_length is not None:
        cfg.max_seq_length = request.max_seq_length
    if request.lora_r is not None:
        cfg.lora_r = request.lora_r
    if request.lora_alpha is not None:
        cfg.lora_alpha = request.lora_alpha
    if request.use_peft is not None:
        cfg.use_peft = request.use_peft
    if request.load_in_4bit is not None:
        cfg.load_in_4bit = request.load_in_4bit

    job = training_service.create_job(cfg)
    background_tasks.add_task(training_service.run_job, job.id)
    return TrainingStartResponse(job_id=job.id, status=job.status)


@router.get("/jobs", response_model=List[TrainingJobResponse], tags=["training"])
def list_jobs():
    """List all training jobs (most recent first)."""
    jobs = training_service.list_jobs()
    return [
        TrainingJobResponse(
            id=j.id,
            status=j.status,
            progress=j.progress,
            started_at=j.started_at,
            finished_at=j.finished_at,
            error=j.error,
            result=j.result,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}", response_model=TrainingJobResponse, tags=["training"])
def get_job(job_id: str):
    """Get the status/result of a specific training job."""
    job = training_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    return TrainingJobResponse(
        id=job.id,
        status=job.status,
        progress=job.progress,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error=job.error,
        result=job.result,
    )

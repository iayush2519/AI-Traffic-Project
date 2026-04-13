"""Model training endpoint (async background task)."""
from __future__ import annotations
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import ModelTrainingRun
from app.models.schemas import TrainRequest, TrainResponse

router = APIRouter(prefix="/model", tags=["model"])


async def _run_training(run_id: int, req: TrainRequest, db: AsyncSession):
    """Background training task."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    try:
        from ml.synthetic_data_gen import generate_traffic_data
        from ml.data_pipeline import run_pipeline

        data_dir  = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        raw_path  = os.path.join(data_dir, "raw_traffic_data.csv")

        if not os.path.exists(raw_path):
            print("[Training] Generating synthetic data …")
            generate_traffic_data(data_dir)

        print("[Training] Running data pipeline …")
        run_pipeline(raw_path)

        metrics = {}

        if req.model_type in ("xgboost", "both"):
            from ml.train_xgboost import train_xgboost
            metrics["xgboost"] = train_xgboost(quick=req.quick)

        if req.model_type in ("lstm", "both"):
            from ml.train_lstm import train_lstm
            metrics["lstm"] = train_lstm()

        from ml.evaluate import generate_report
        generate_report()

        # Update DB
        async with db.begin():
            result = await db.get(ModelTrainingRun, run_id)
            if result:
                result.status      = "done"
                result.finished_at = datetime.utcnow()
                result.metrics_json = json.dumps({"summary": "Training complete"})

        print(f"[Training] Run {run_id} completed.")

    except Exception as e:
        print(f"[Training] Run {run_id} FAILED: {e}")
        async with db.begin():
            result = await db.get(ModelTrainingRun, run_id)
            if result:
                result.status    = "failed"
                result.error_msg = str(e)
                result.finished_at = datetime.utcnow()


@router.post("/train", response_model=TrainResponse)
async def train_model(req: TrainRequest,
                       background_tasks: BackgroundTasks,
                       db: AsyncSession = Depends(get_db)):
    """Trigger async model training."""
    run = ModelTrainingRun(
        model_type = req.model_type,
        status     = "running",
        started_at = datetime.utcnow(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    background_tasks.add_task(_run_training, run.id, req, db)

    return TrainResponse(
        run_id  = run.id,
        status  = "running",
        message = f"Training started (run_id={run.id}). Poll /model/status/{run.id}",
    )


@router.get("/status/{run_id}")
async def training_status(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await db.get(ModelTrainingRun, run_id)
    if not run:
        return {"error": "Run not found"}
    return {
        "run_id":      run.id,
        "status":      run.status,
        "model_type":  run.model_type,
        "started_at":  run.started_at,
        "finished_at": run.finished_at,
        "error":       run.error_msg,
    }

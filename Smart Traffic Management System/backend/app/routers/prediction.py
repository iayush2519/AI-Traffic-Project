"""Congestion prediction endpoints."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_service import predict
from app.services.simulation_service import get_intersection_state

router = APIRouter(prefix="/predict", tags=["prediction"])

VALID_HORIZONS = {"5min", "15min", "30min"}
VALID_MODELS   = {"xgboost", "lstm"}


@router.post("/congestion", response_model=PredictionResponse)
async def predict_congestion(req: PredictionRequest):
    """Predict congestion level for an intersection."""
    if req.horizon not in VALID_HORIZONS:
        raise HTTPException(400, f"horizon must be one of {VALID_HORIZONS}")
    if req.model_name not in VALID_MODELS:
        raise HTTPException(400, f"model_name must be one of {VALID_MODELS}")

    # Get current reading for this intersection
    state = get_intersection_state(req.intersection_id)
    reading = state if state else {"traffic_density": 0.4, "average_speed": 35.0,
                                    "vehicle_count": 30, "timestamp": datetime.now()}

    result = predict(reading, model_name=req.model_name, horizon=req.horizon)

    return PredictionResponse(
        intersection_id  = req.intersection_id,
        model_name       = req.model_name,
        horizon          = req.horizon,
        predicted_class  = result["predicted_class"],
        predicted_score  = result["predicted_score"],
        confidence       = result["confidence"],
        class_probs      = result["class_probs"],
        timestamp        = datetime.now(timezone.utc),
    )


@router.get("/congestion/{intersection_id}")
async def quick_predict(intersection_id: str,
                         model: str = "xgboost",
                         horizon: str = "15min"):
    """Quick GET endpoint for single-intersection prediction."""
    req = PredictionRequest(intersection_id=intersection_id,
                             model_name=model, horizon=horizon)
    return await predict_congestion(req)


@router.get("/all")
async def predict_all(model: str = "xgboost", horizon: str = "15min"):
    """Batch prediction for all intersections."""
    from app.services.simulation_service import get_current_state, INTERSECTIONS
    states  = get_current_state()
    results = []
    for state in states:
        res = predict(state, model_name=model, horizon=horizon)
        results.append({
            "intersection_id":  state["intersection_id"],
            "horizon":          horizon,
            "model":            model,
            **res,
        })
    return results

"""Pydantic request/response schemas."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Ingest ──────────────────────────────────────────────────────────────────
class TrafficReadingIn(BaseModel):
    intersection_id:  str
    road_segment_id:  str = ""
    lat:              float = 34.0
    lon:              float = -118.25
    road_class:       str  = "arterial"
    vehicle_count:    int  = Field(ge=0)
    average_speed:    float = Field(ge=0)
    occupancy:        float = Field(ge=0, le=100)
    flow:             float = Field(ge=0, default=0)
    queue_length:     float = Field(ge=0, default=0)
    waiting_time:     float = Field(ge=0, default=0)
    traffic_density:  float = Field(ge=0, le=1)
    weather_condition: str  = "clear"
    timestamp:        Optional[datetime] = None


class TrafficReadingOut(TrafficReadingIn):
    id:               int
    timestamp:        datetime
    congestion_label: str
    congestion_score: float


# ─── Prediction ───────────────────────────────────────────────────────────────
class PredictionRequest(BaseModel):
    intersection_id: str
    model_name:      str = "xgboost"   # xgboost | lstm
    horizon:         str = "15min"     # 5min | 15min | 30min


class PredictionResponse(BaseModel):
    intersection_id:  str
    model_name:       str
    horizon:          str
    predicted_class:  str
    predicted_score:  float
    confidence:       float
    class_probs:      dict[str, float]
    timestamp:        datetime


# ─── Signal ───────────────────────────────────────────────────────────────────
class SignalOptimizeRequest(BaseModel):
    intersection_id:   str
    congestion_ns:     float = Field(ge=0, le=1, description="North-South congestion score")
    congestion_ew:     float = Field(ge=0, le=1, description="East-West congestion score")
    vehicle_count_ns:  int   = Field(ge=0, default=20)
    vehicle_count_ew:  int   = Field(ge=0, default=20)
    queue_length_ns:   float = Field(ge=0, default=5)
    queue_length_ew:   float = Field(ge=0, default=5)
    waiting_time_ns:   float = Field(ge=0, default=30)
    waiting_time_ew:   float = Field(ge=0, default=30)
    priority_lane:     Optional[str] = None  # "NS" | "EW" | None
    hour_of_day:       int   = Field(ge=0, le=23, default=12)


class SignalTimingOut(BaseModel):
    intersection_id:  str
    phase_ns_green:   int
    phase_ew_green:   int
    yellow_time:      int
    cycle_time:       int
    mode:             str
    reason:           str
    timestamp:        datetime


# ─── Traffic Status ───────────────────────────────────────────────────────────
class IntersectionStatus(BaseModel):
    intersection_id:  str
    intersection_name: Optional[str] = None
    lat:              float
    lon:              float
    road_class:       str
    vehicle_count:    int
    average_speed:    float
    occupancy:        float
    queue_length:     float
    waiting_time:     float
    traffic_density:  float
    congestion_label: str
    congestion_score: float
    weather_condition: str
    timestamp:        datetime
    # Signal info
    phase_ns_green:   Optional[int] = None
    phase_ew_green:   Optional[int] = None
    cycle_time:       Optional[int] = None
    signal_mode:      Optional[str] = None
    # Prediction
    predicted_label_15min: Optional[str] = None
    predicted_score_15min: Optional[float] = None
    confidence_15min:      Optional[float] = None


# ─── Training ─────────────────────────────────────────────────────────────────
class TrainRequest(BaseModel):
    model_type: str = "both"   # xgboost | lstm | both
    quick:      bool = True    # Quick mode skips grid search


class TrainResponse(BaseModel):
    run_id:     int
    status:     str
    message:    str


# ─── Health ───────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status:         str
    models_loaded:  dict[str, bool]
    db_connected:   bool
    version:        str = "1.0.0"

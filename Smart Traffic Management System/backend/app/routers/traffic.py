"""Traffic status and data ingestion endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.db_models import TrafficReading
from app.models.schemas import TrafficReadingIn, IntersectionStatus
from app.services.simulation_service import get_current_state, get_intersection_state

router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.get("/status", response_model=List[IntersectionStatus])
async def traffic_status():
    """Get current simulated traffic status for all intersections."""
    return get_current_state()


@router.get("/status/{intersection_id}", response_model=IntersectionStatus)
async def intersection_status(intersection_id: str):
    state = get_intersection_state(intersection_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Intersection {intersection_id} not found")
    return state


@router.post("/ingest", status_code=201)
async def ingest_reading(reading: TrafficReadingIn, db: AsyncSession = Depends(get_db)):
    """Ingest a single traffic sensor reading into the database."""
    ts = reading.timestamp or datetime.utcnow()
    density = reading.traffic_density

    # Derive congestion label
    if density < 0.25:   label, score = "low", density
    elif density < 0.50: label, score = "medium", density
    elif density < 0.75: label, score = "high", density
    else:                label, score = "severe", density

    obj = TrafficReading(
        timestamp        = ts,
        intersection_id  = reading.intersection_id,
        road_segment_id  = reading.road_segment_id,
        lat              = reading.lat,
        lon              = reading.lon,
        road_class       = reading.road_class,
        vehicle_count    = reading.vehicle_count,
        average_speed    = reading.average_speed,
        occupancy        = reading.occupancy,
        flow             = reading.flow,
        queue_length     = reading.queue_length,
        waiting_time     = reading.waiting_time,
        traffic_density  = reading.traffic_density,
        weather_condition= reading.weather_condition,
        day_of_week      = ts.weekday(),
        hour_of_day      = ts.hour,
        is_weekend       = ts.weekday() >= 5,
        congestion_label = label,
        congestion_score = score,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return {"id": obj.id, "status": "ingested", "congestion_label": label}


@router.get("/history/{intersection_id}")
async def intersection_history(intersection_id: str, limit: int = 288,
                               db: AsyncSession = Depends(get_db)):
    """Get historical readings (default last 24h @ 5-min intervals)."""
    result = await db.execute(
        select(TrafficReading)
        .where(TrafficReading.intersection_id == intersection_id)
        .order_by(desc(TrafficReading.timestamp))
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "timestamp":       r.timestamp,
            "vehicle_count":   r.vehicle_count,
            "average_speed":   r.average_speed,
            "traffic_density": r.traffic_density,
            "congestion_label":r.congestion_label,
            "congestion_score":r.congestion_score,
            "queue_length":    r.queue_length,
            "waiting_time":    r.waiting_time,
        }
        for r in reversed(rows)
    ]

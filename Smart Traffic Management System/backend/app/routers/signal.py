"""Signal optimization endpoints."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter

from app.models.schemas import SignalOptimizeRequest, SignalTimingOut
from app.services.signal_service import optimize_signal
from app.services.simulation_service import get_current_state

router = APIRouter(prefix="/signal", tags=["signal"])


@router.post("/optimize", response_model=SignalTimingOut)
async def optimize_signal_timing(req: SignalOptimizeRequest):
    """Compute optimized signal timing for an intersection."""
    return optimize_signal(req)


@router.get("/optimize/{intersection_id}", response_model=SignalTimingOut)
async def optimize_from_state(intersection_id: str):
    """Auto-optimize signal timing using current simulated state."""
    from app.services.simulation_service import get_intersection_state
    state = get_intersection_state(intersection_id)
    if not state:
        density = 0.4
        vc, ql, wt = 30, 5.0, 25.0
    else:
        density = state["traffic_density"]
        vc  = state["vehicle_count"]
        ql  = state["queue_length"]
        wt  = state["waiting_time"]

    # For demo: split density randomly between NS/EW with ±15% variance
    import random
    split = random.uniform(0.35, 0.65)
    ns_d  = min(0.99, density * split * 2)
    ew_d  = min(0.99, density * (1 - split) * 2)

    req = SignalOptimizeRequest(
        intersection_id   = intersection_id,
        congestion_ns     = ns_d,
        congestion_ew     = ew_d,
        vehicle_count_ns  = int(vc * split),
        vehicle_count_ew  = int(vc * (1 - split)),
        queue_length_ns   = ql * split,
        queue_length_ew   = ql * (1 - split),
        waiting_time_ns   = wt,
        waiting_time_ew   = wt,
        hour_of_day       = datetime.now().hour,
    )
    return optimize_signal(req)


@router.get("/all", response_model=List[SignalTimingOut])
async def optimize_all():
    """Batch signal optimization for all intersections."""
    results = []
    for s in get_current_state():
        timing = await optimize_from_state(s["intersection_id"])
        results.append(timing)
    return results

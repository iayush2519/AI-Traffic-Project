"""
Live traffic simulation service.
Generates realistic traffic states for all intersections every 5 seconds.
"""
from __future__ import annotations
import asyncio
import math
import random
from datetime import datetime, timezone

import numpy as np

from app.websocket_manager import ws_manager

random.seed(None)  # Non-deterministic for live feel

INTERSECTIONS = [
    {"id": f"INT_{i:03d}", "name": f"Intersection {i}",
     "lat": 33.90 + (i % 5) * 0.04 + random.uniform(-0.01, 0.01),
     "lon": -118.40 + (i // 5) * 0.075 + random.uniform(-0.01, 0.01),
     "road_class": ["arterial", "highway", "local"][(i % 3)]}
    for i in range(1, 21)
]

_state: dict[str, dict] = {}
_prev_density: dict[str, float] = {}


def _demand_multiplier(hour: int) -> float:
    profile = [0.20, 0.18, 0.15, 0.14, 0.15, 0.22, 0.40, 0.55,
               0.65, 0.72, 0.75, 0.78, 0.80, 0.77, 0.73, 0.70,
               0.72, 0.68, 0.60, 0.52, 0.45, 0.38, 0.30, 0.24]
    return profile[hour]


def _label(density: float) -> str:
    if density < 0.25:   return "low"
    elif density < 0.50: return "medium"
    elif density < 0.75: return "high"
    else:                return "severe"


def _simulate_step() -> list[dict]:
    now  = datetime.now(timezone.utc)
    hour = now.hour
    dm   = _demand_multiplier(hour)

    results = []
    for inter in INTERSECTIONS:
        iid = inter["id"]
        prev = _prev_density.get(iid, dm)

        # Smooth random walk
        noise   = random.gauss(0, 0.025)
        density = 0.85 * prev + 0.15 * dm + noise
        density = max(0.05, min(0.98, density))
        _prev_density[iid] = density

        rc = inter["road_class"]
        base_speed = {"highway": 65.0, "arterial": 40.0, "local": 25.0}[rc]
        speed = base_speed * (1 - 0.85 * density) + random.gauss(0, 1.2)
        speed = max(2.0, speed)

        capacity    = {"highway": 120, "arterial": 60, "local": 30}[rc]
        vc          = max(0, int(capacity * density + random.gauss(0, 2)))
        occupancy   = round(density * 100, 1)
        queue_len   = round(density * 25 + abs(random.gauss(0, 2)), 1)
        waiting     = round(queue_len * 1.8 + abs(random.gauss(0, 3)), 1)
        flow        = round(vc * (speed / base_speed) * 12, 1)
        cong_score  = round(density, 4)
        cong_label  = _label(density)

        record = {
            "intersection_id":   iid,
            "intersection_name": inter["name"],
            "lat":               inter["lat"],
            "lon":               inter["lon"],
            "road_class":        rc,
            "vehicle_count":     vc,
            "average_speed":     round(speed, 2),
            "occupancy":         occupancy,
            "flow":              flow,
            "queue_length":      queue_len,
            "waiting_time":      waiting,
            "traffic_density":   density,
            "weather_condition": "clear",
            "congestion_label":  cong_label,
            "congestion_score":  cong_score,
            "timestamp":         now.isoformat(),
            # Quick rule-based signal
            "phase_ns_green":    max(10, min(70, int(35 + (density - 0.5) * 40))),
            "phase_ew_green":    max(10, min(70, int(35 - (density - 0.5) * 40))),
            "cycle_time":        90,
            "signal_mode":       "adaptive",
            "predicted_label_15min": _label(min(0.98, density + 0.05)),
            "predicted_score_15min": round(min(0.98, density + 0.05), 4),
            "confidence_15min":  round(0.72 + random.uniform(-0.05, 0.05), 3),
        }
        _state[iid] = record
        results.append(record)

    return results


async def simulation_loop():
    """Background task: simulate + broadcast every 5 seconds."""
    print("[Sim] Simulation loop started")
    while True:
        try:
            snapshot = _simulate_step()
            if ws_manager.count > 0:
                await ws_manager.broadcast({
                    "type": "traffic_update",
                    "data": snapshot,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"[Sim] Error: {e}")
        await asyncio.sleep(5)


def get_current_state() -> list[dict]:
    if not _state:
        _simulate_step()
    return list(_state.values())


def get_intersection_state(iid: str) -> dict | None:
    if not _state:
        _simulate_step()
    return _state.get(iid)

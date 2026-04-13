"""
Adaptive Traffic Signal Controller
Rule-based + optimization logic driven by congestion predictions.

Constraints:
  - MIN_GREEN = 10s  MAX_GREEN = 70s
  - YELLOW    = 3s  (fixed)
  - MIN_CYCLE = 60s  MAX_CYCLE = 150s
"""
from __future__ import annotations
import math
from datetime import datetime
from app.models.schemas import SignalOptimizeRequest, SignalTimingOut

# ── Hard constraints ───────────────────────────────────────────────────────────
MIN_GREEN  = 10
MAX_GREEN  = 70
YELLOW     = 3
MIN_CYCLE  = 60
MAX_CYCLE  = 150
BASE_CYCLE = 90   # standard off-peak cycle

# Congestion thresholds
HIGH_THRESH   = 0.65
SEVERE_THRESH = 0.80
BALANCE_THRESH = 0.15   # |NS-EW| < 0.15 → balanced

RUSH_HOURS = list(range(7, 10)) + list(range(17, 20))


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def _compute_weights(req: SignalOptimizeRequest) -> tuple[float, float]:
    """Weighted demand score for each direction."""
    def score(density: float, count: int, queue: float, wait: float) -> float:
        return (0.40 * density +
                0.25 * min(count / 120, 1.0) +
                0.20 * min(queue / 30, 1.0) +
                0.15 * min(wait  / 120, 1.0))

    ns = score(req.congestion_ns, req.vehicle_count_ns,
               req.queue_length_ns, req.waiting_time_ns)
    ew = score(req.congestion_ew, req.vehicle_count_ew,
               req.queue_length_ew, req.waiting_time_ew)
    return ns, ew


def optimize_signal(req: SignalOptimizeRequest) -> SignalTimingOut:
    ns_w, ew_w = _compute_weights(req)
    total_w    = ns_w + ew_w if (ns_w + ew_w) > 0 else 1.0

    # Choose cycle time (longer during rush hours)
    is_rush = req.hour_of_day in RUSH_HOURS
    cycle   = BASE_CYCLE + (15 if is_rush else 0)

    # Available green time (subtract yellows for 2 phases)
    avail_green = cycle - 2 * YELLOW

    # Start with proportional split
    ns_green_raw = avail_green * (ns_w / total_w)
    ew_green_raw = avail_green * (ew_w / total_w)

    mode   = "adaptive"
    reason = f"Adaptive: NS_weight={ns_w:.2f} EW_weight={ew_w:.2f}"

    # ── Emergency / priority override ─────────────────────────────────────────
    if req.priority_lane == "NS":
        ns_green_raw = avail_green * 0.80
        ew_green_raw = avail_green * 0.20
        mode   = "emergency"
        reason = "Emergency priority: NS lane override"
    elif req.priority_lane == "EW":
        ns_green_raw = avail_green * 0.20
        ew_green_raw = avail_green * 0.80
        mode   = "emergency"
        reason = "Emergency priority: EW lane override"

    # ── Severe congestion boost ────────────────────────────────────────────────
    elif req.congestion_ns >= SEVERE_THRESH and req.congestion_ew < HIGH_THRESH:
        ns_green_raw = avail_green * 0.75
        ew_green_raw = avail_green * 0.25
        reason = f"Severe NS congestion ({req.congestion_ns:.2f}) → boosted NS green"
    elif req.congestion_ew >= SEVERE_THRESH and req.congestion_ns < HIGH_THRESH:
        ns_green_raw = avail_green * 0.25
        ew_green_raw = avail_green * 0.75
        reason = f"Severe EW congestion ({req.congestion_ew:.2f}) → boosted EW green"

    # ── Balanced mode ──────────────────────────────────────────────────────────
    elif abs(req.congestion_ns - req.congestion_ew) < BALANCE_THRESH:
        ns_green_raw = ew_green_raw = avail_green / 2
        mode   = "balanced"
        reason = f"Balanced congestion (diff={abs(req.congestion_ns - req.congestion_ew):.2f})"

    # ── Apply hard constraints ─────────────────────────────────────────────────
    ns_green = int(_clamp(ns_green_raw, MIN_GREEN, MAX_GREEN))
    ew_green = int(_clamp(ew_green_raw, MIN_GREEN, MAX_GREEN))

    # Recompute actual cycle
    actual_cycle = ns_green + ew_green + 2 * YELLOW
    actual_cycle = int(_clamp(actual_cycle, MIN_CYCLE, MAX_CYCLE))

    return SignalTimingOut(
        intersection_id = req.intersection_id,
        phase_ns_green  = ns_green,
        phase_ew_green  = ew_green,
        yellow_time     = YELLOW,
        cycle_time      = actual_cycle,
        mode            = mode,
        reason          = reason,
        timestamp       = datetime.utcnow(),
    )

"""
Synthetic Traffic Data Generator
Generates realistic traffic data for 20 intersections over 6 months,
modeled after METR-LA statistics (speed, flow, occupancy patterns).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# ── Configuration ─────────────────────────────────────────────────────────────
NUM_INTERSECTIONS = 20
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 7, 1)
INTERVAL_MINUTES = 5
RANDOM_SEED = 42

# Los Angeles lat/lon bounding box (METR-LA area)
LAT_MIN, LAT_MAX = 33.90, 34.10
LON_MIN, LON_MAX = -118.40, -118.10

INTERSECTIONS = [
    {"id": f"INT_{i:03d}", "name": f"Intersection {i}",
     "lat": np.random.uniform(LAT_MIN, LAT_MAX),
     "lon": np.random.uniform(LON_MIN, LON_MAX),
     "road_class": np.random.choice(["arterial", "highway", "local"], p=[0.5, 0.3, 0.2])}
    for i in range(1, NUM_INTERSECTIONS + 1)
]

WEATHER_CONDITIONS = ["clear", "cloudy", "rain", "fog", "drizzle"]

# ── Helper functions ───────────────────────────────────────────────────────────

def demand_multiplier(hour: int, dow: int) -> float:
    """Time-of-day + day-of-week demand curve."""
    is_weekend = dow >= 5

    if is_weekend:
        # Moderate midday peak
        profile = [0.20, 0.18, 0.15, 0.14, 0.15, 0.22, 0.40, 0.55,
                   0.65, 0.72, 0.75, 0.78, 0.80, 0.77, 0.73, 0.70,
                   0.72, 0.68, 0.60, 0.52, 0.45, 0.38, 0.30, 0.24]
    else:
        # Weekday AM/PM peaks
        profile = [0.15, 0.12, 0.10, 0.10, 0.14, 0.28, 0.55, 0.88,
                   0.95, 0.75, 0.65, 0.68, 0.72, 0.70, 0.73, 0.82,
                   0.95, 0.90, 0.78, 0.65, 0.52, 0.42, 0.32, 0.22]
    return profile[hour]


def base_speed(road_class: str) -> float:
    """Free-flow speed by road class (mph)."""
    return {"highway": 65.0, "arterial": 40.0, "local": 25.0}[road_class]


def congestion_label(density: float) -> str:
    """Map density [0,1] → congestion label."""
    if density < 0.25:
        return "low"
    elif density < 0.50:
        return "medium"
    elif density < 0.75:
        return "high"
    else:
        return "severe"


def congestion_score(density: float) -> float:
    """Smooth congestion score [0, 1]."""
    return float(np.clip(density, 0.0, 1.0))


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_traffic_data(output_dir: str = "data") -> pd.DataFrame:
    np.random.seed(RANDOM_SEED)
    os.makedirs(output_dir, exist_ok=True)

    timestamps = pd.date_range(start=START_DATE, end=END_DATE, freq=f"{INTERVAL_MINUTES}min", inclusive="left")
    print(f"[DataGen] Generating {len(timestamps)} timesteps × {NUM_INTERSECTIONS} intersections …")

    records = []
    weather_cache: dict[str, str] = {}  # date_str → weather

    for ts in timestamps:
        date_str = ts.strftime("%Y-%m-%d")
        if date_str not in weather_cache:
            weather_cache[date_str] = np.random.choice(
                WEATHER_CONDITIONS, p=[0.55, 0.20, 0.10, 0.08, 0.07]
            )
        weather = weather_cache[date_str]
        weather_factor = {"clear": 1.0, "cloudy": 0.97, "drizzle": 0.88,
                          "rain": 0.78, "fog": 0.70}[weather]

        hour = ts.hour
        dow  = ts.dayofweek
        dm   = demand_multiplier(hour, dow)

        # Simulate random incidents hourly
        incident = np.random.random() < 0.03  # 3% chance per 5-min slot

        for inter in INTERSECTIONS:
            rc  = inter["road_class"]
            bs  = base_speed(rc)

            # Density driven by demand × weather × noise
            noise   = np.random.normal(0, 0.04)
            density = np.clip(dm * weather_factor + noise + (0.30 if incident else 0), 0, 1)

            # Speed inversely proportional to density (Greenshields model)
            speed = bs * (1 - 0.85 * density) + np.random.normal(0, 1.5)
            speed = max(2.0, speed)

            # Max vehicles capacity by road class
            capacity = {"highway": 120, "arterial": 60, "local": 30}[rc]
            vehicle_count = int(capacity * density + np.random.normal(0, 2))
            vehicle_count = max(0, vehicle_count)

            occupancy   = round(density * 100, 2)
            queue_len   = round(density * 25 + np.random.exponential(2) * density, 1)
            waiting_time = round(queue_len * 1.8 + np.random.exponential(3) * density, 1)
            flow        = round(vehicle_count * (speed / bs) * 12, 1)  # vehicles/hour

            records.append({
                "timestamp":        ts,
                "intersection_id":  inter["id"],
                "intersection_name":inter["name"],
                "road_segment_id":  f"SEG_{inter['id']}",
                "lat":              round(inter["lat"], 6),
                "lon":              round(inter["lon"], 6),
                "road_class":       rc,
                "vehicle_count":    vehicle_count,
                "average_speed":    round(speed, 2),
                "occupancy":        occupancy,
                "flow":             flow,
                "queue_length":     queue_len,
                "waiting_time":     waiting_time,
                "traffic_density":  round(density, 4),
                "weather_condition":weather,
                "day_of_week":      dow,
                "hour_of_day":      hour,
                "is_weekend":       int(dow >= 5),
                "is_incident":      int(incident),
                "congestion_label": congestion_label(density),
                "congestion_score": congestion_score(density),
            })

    df = pd.DataFrame(records)
    out_path = os.path.join(output_dir, "raw_traffic_data.csv")
    df.to_csv(out_path, index=False)
    print(f"[DataGen] Saved {len(df):,} rows → {out_path}")
    return df


def get_intersection_metadata() -> pd.DataFrame:
    return pd.DataFrame(INTERSECTIONS)


if __name__ == "__main__":
    generate_traffic_data(output_dir=os.path.join(os.path.dirname(__file__), "..", "data"))

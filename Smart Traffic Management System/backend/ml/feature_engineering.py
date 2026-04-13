"""
Feature Engineering Pipeline
Creates temporal, lag, and rolling features for congestion prediction.
"""

import numpy as np
import pandas as pd


LABEL_MAP = {"low": 0, "medium": 1, "high": 2, "severe": 3}
LABEL_INV = {v: k for k, v in LABEL_MAP.items()}

NUMERIC_FEATURES = [
    "vehicle_count", "average_speed", "occupancy", "flow",
    "queue_length", "waiting_time", "traffic_density",
]

TIME_FEATURES = [
    "hour_sin", "hour_cos", "dow_sin", "dow_cos",
    "is_weekend", "is_rush_hour",
]

LAG_COLS = ["traffic_density", "average_speed", "vehicle_count", "queue_length"]
LAG_STEPS = [1, 3, 6, 12]          # × 5 min → 5, 15, 30, 60 min
ROLLING_WINDOWS = [3, 6, 12]       # × 5 min → 15, 30, 60 min


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    h = df["hour_of_day"]
    d = df["day_of_week"]

    df["hour_sin"] = np.sin(2 * np.pi * h / 24)
    df["hour_cos"] = np.cos(2 * np.pi * h / 24)
    df["dow_sin"]  = np.sin(2 * np.pi * d / 7)
    df["dow_cos"]  = np.cos(2 * np.pi * d / 7)
    df["is_rush_hour"] = h.apply(lambda x: 1 if (7 <= x <= 9 or 17 <= x <= 19) else 0)
    df["minute_of_day"] = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag features per intersection (sorted by time)."""
    df = df.sort_values(["intersection_id", "timestamp"]).copy()
    for col in LAG_COLS:
        for lag in LAG_STEPS:
            df[f"{col}_lag{lag}"] = (
                df.groupby("intersection_id")[col].shift(lag)
            )
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling mean/std per intersection."""
    df = df.sort_values(["intersection_id", "timestamp"]).copy()
    for col in ["traffic_density", "average_speed", "vehicle_count"]:
        for win in ROLLING_WINDOWS:
            rolled = df.groupby("intersection_id")[col].transform(
                lambda x: x.shift(1).rolling(win, min_periods=1).mean()
            )
            df[f"{col}_roll{win}_mean"] = rolled
            df[f"{col}_roll{win}_std"] = df.groupby("intersection_id")[col].transform(
                lambda x: x.shift(1).rolling(win, min_periods=1).std().fillna(0)
            )
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Encode road class
    df = pd.get_dummies(df, columns=["road_class"], prefix="rc")
    # Encode weather
    df = pd.get_dummies(df, columns=["weather_condition"], prefix="wx")
    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["congestion_class"] = df["congestion_label"].map(LABEL_MAP)
    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return all feature columns (exclude metadata/target cols)."""
    exclude = {
        "timestamp", "intersection_id", "intersection_name",
        "road_segment_id", "lat", "lon", "road_class", "weather_condition",
        "congestion_label", "congestion_class", "congestion_score",
        "is_incident",
    }
    return [c for c in df.columns if c not in exclude]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_time_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = encode_categoricals(df)
    df = encode_target(df)
    return df

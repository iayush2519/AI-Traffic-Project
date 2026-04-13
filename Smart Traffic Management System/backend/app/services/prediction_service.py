"""
Prediction Service — wraps XGBoost and LSTM models.
Handles feature construction for a single intersection reading.
"""
from __future__ import annotations
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models_trained")

LABEL_MAP = {0: "low", 1: "medium", 2: "high", 3: "severe"}

# Cache loaded models
_xgb_cache:  dict[str, dict] = {}
_lstm_cache: dict[str, dict] = {}
_models_ready = {"xgboost": False, "lstm": False}


def _load_xgb(horizon: str):
    if horizon not in _xgb_cache:
        path = os.path.join(MODEL_DIR, f"xgboost_{horizon}.pkl")
        if os.path.exists(path):
            _xgb_cache[horizon] = joblib.load(path)
    return _xgb_cache.get(horizon)


def _load_lstm(horizon: str):
    if horizon not in _lstm_cache:
        keras_path = os.path.join(MODEL_DIR, f"lstm_{horizon}.keras")
        meta_path  = os.path.join(MODEL_DIR, f"lstm_{horizon}_meta.pkl")
        if os.path.exists(keras_path) and os.path.exists(meta_path):
            try:
                import tensorflow as tf
                model = tf.keras.models.load_model(keras_path)
                meta  = joblib.load(meta_path)
                _lstm_cache[horizon] = {"model": model, **meta}
            except Exception as e:
                print(f"[PredService] LSTM load failed: {e}")
    return _lstm_cache.get(horizon)


def load_all_models():
    """Pre-load all models on startup."""
    for h in ["5min", "15min", "30min"]:
        if _load_xgb(h):
            _models_ready["xgboost"] = True
    for h in ["5min", "15min", "30min"]:
        if _load_lstm(h):
            _models_ready["lstm"] = True
    print(f"[PredService] Models ready: {_models_ready}")


def get_models_status() -> dict[str, bool]:
    return dict(_models_ready)


def _build_input_row(reading: dict) -> pd.DataFrame:
    """Build a single-row DataFrame with engineered features."""
    ts = reading.get("timestamp") or datetime.utcnow()
    if isinstance(ts, str):
        ts = pd.to_datetime(ts)

    hour = ts.hour
    dow  = ts.weekday() if hasattr(ts, "weekday") else ts.dayofweek

    row = {
        "vehicle_count":    reading.get("vehicle_count", 30),
        "average_speed":    reading.get("average_speed", 35.0),
        "occupancy":        reading.get("occupancy", 40.0),
        "flow":             reading.get("flow", 200.0),
        "queue_length":     reading.get("queue_length", 5.0),
        "waiting_time":     reading.get("waiting_time", 25.0),
        "traffic_density":  reading.get("traffic_density", 0.4),
        "hour_of_day":      hour,
        "day_of_week":      dow,
        "is_weekend":       int(dow >= 5),
        "hour_sin":         np.sin(2 * np.pi * hour / 24),
        "hour_cos":         np.cos(2 * np.pi * hour / 24),
        "dow_sin":          np.sin(2 * np.pi * dow / 7),
        "dow_cos":          np.cos(2 * np.pi * dow / 7),
        "is_rush_hour":     int(7 <= hour <= 9 or 17 <= hour <= 19),
        "minute_of_day":    hour * 60 + ts.minute if hasattr(ts, "minute") else 0,
        # Lag features (approximate with current value for single-reading inference)
        "traffic_density_lag1":  reading.get("traffic_density", 0.4),
        "traffic_density_lag3":  reading.get("traffic_density", 0.4),
        "traffic_density_lag6":  reading.get("traffic_density", 0.4),
        "traffic_density_lag12": reading.get("traffic_density", 0.4),
        "average_speed_lag1":    reading.get("average_speed", 35.0),
        "average_speed_lag3":    reading.get("average_speed", 35.0),
        "average_speed_lag6":    reading.get("average_speed", 35.0),
        "average_speed_lag12":   reading.get("average_speed", 35.0),
        "vehicle_count_lag1":    reading.get("vehicle_count", 30),
        "vehicle_count_lag3":    reading.get("vehicle_count", 30),
        "vehicle_count_lag6":    reading.get("vehicle_count", 30),
        "vehicle_count_lag12":   reading.get("vehicle_count", 30),
        "queue_length_lag1":     reading.get("queue_length", 5.0),
        "queue_length_lag3":     reading.get("queue_length", 5.0),
        "queue_length_lag6":     reading.get("queue_length", 5.0),
        "queue_length_lag12":    reading.get("queue_length", 5.0),
        # Rolling (approximate)
        "traffic_density_roll3_mean":  reading.get("traffic_density", 0.4),
        "traffic_density_roll3_std":   0.02,
        "traffic_density_roll6_mean":  reading.get("traffic_density", 0.4),
        "traffic_density_roll6_std":   0.03,
        "traffic_density_roll12_mean": reading.get("traffic_density", 0.4),
        "traffic_density_roll12_std":  0.04,
        "average_speed_roll3_mean":    reading.get("average_speed", 35.0),
        "average_speed_roll3_std":     2.0,
        "average_speed_roll6_mean":    reading.get("average_speed", 35.0),
        "average_speed_roll6_std":     3.0,
        "average_speed_roll12_mean":   reading.get("average_speed", 35.0),
        "average_speed_roll12_std":    4.0,
        "vehicle_count_roll3_mean":    reading.get("vehicle_count", 30),
        "vehicle_count_roll3_std":     3.0,
        "vehicle_count_roll6_mean":    reading.get("vehicle_count", 30),
        "vehicle_count_roll6_std":     4.0,
        "vehicle_count_roll12_mean":   reading.get("vehicle_count", 30),
        "vehicle_count_roll12_std":    5.0,
    }

    # Road class dummies
    for rc in ["arterial", "highway", "local"]:
        row[f"rc_{rc}"] = int(reading.get("road_class", "arterial") == rc)

    # Weather dummies
    for wx in ["clear", "cloudy", "drizzle", "fog", "rain"]:
        row[f"wx_{wx}"] = int(reading.get("weather_condition", "clear") == wx)

    return pd.DataFrame([row])


def predict(reading: dict, model_name: str = "xgboost",
            horizon: str = "15min") -> dict:
    """Run inference for a single intersection reading."""

    if model_name == "xgboost":
        artifact = _load_xgb(horizon)
        if not artifact:
            # Fallback: rule-based estimation
            return _rule_based_predict(reading, horizon)

        model    = artifact["model"]
        features = artifact["features"]
        df = _build_input_row(reading)
        # Select and order matching features
        available = [f for f in features if f in df.columns]
        missing   = [f for f in features if f not in df.columns]
        for f in missing:
            df[f] = 0.0
        X = df[features].values

        proba  = model.predict_proba(X)[0]
        cls_id = int(np.argmax(proba))
        label  = LABEL_MAP[cls_id]
        conf   = float(proba[cls_id])
        score  = float(cls_id / 3)

        return {
            "predicted_class": label,
            "predicted_score": score,
            "confidence":      conf,
            "class_probs":     {LABEL_MAP[i]: float(p) for i, p in enumerate(proba)},
        }

    elif model_name == "lstm":
        artifact = _load_lstm(horizon)
        if not artifact:
            return _rule_based_predict(reading, horizon)

        # For single reading, duplicate the row to form a minimal sequence
        model    = artifact["model"]
        features = artifact["features"]
        seq_len  = artifact["seq_len"]

        df = _build_input_row(reading)
        available = [f for f in features if f in df.columns]
        for f in features:
            if f not in df.columns:
                df[f] = 0.0
        row_vec = df[features].values[0]
        X = np.tile(row_vec, (seq_len, 1))[np.newaxis].astype(np.float32)

        proba  = model.predict(X, verbose=0)[0]
        cls_id = int(np.argmax(proba))
        label  = LABEL_MAP[cls_id]
        conf   = float(proba[cls_id])
        score  = float(cls_id / 3)

        return {
            "predicted_class": label,
            "predicted_score": score,
            "confidence":      conf,
            "class_probs":     {LABEL_MAP[i]: float(p) for i, p in enumerate(proba)},
        }

    return _rule_based_predict(reading, horizon)


def _rule_based_predict(reading: dict, horizon: str) -> dict:
    """Deterministic rule-based fallback when no model is loaded."""
    density = float(reading.get("traffic_density", 0.4))
    speed   = float(reading.get("average_speed", 35.0))

    # Adjust for horizon (further out → slightly higher uncertainty)
    horizon_boost = {"5min": 0.0, "15min": 0.03, "30min": 0.07}.get(horizon, 0.03)
    density = min(1.0, density + horizon_boost)

    if density < 0.25:   cls_id, label = 0, "low"
    elif density < 0.50: cls_id, label = 1, "medium"
    elif density < 0.75: cls_id, label = 2, "high"
    else:                cls_id, label = 3, "severe"

    conf = 0.70 + 0.10 * (1 - abs(density - cls_id * 0.25 - 0.125) / 0.25)
    proba = [0.0, 0.0, 0.0, 0.0]
    proba[cls_id] = conf
    remainder = 1 - conf
    for i in range(4):
        if i != cls_id:
            proba[i] = remainder / 3

    return {
        "predicted_class": label,
        "predicted_score": float(cls_id / 3),
        "confidence":      float(conf),
        "class_probs":     {LABEL_MAP[i]: float(p) for i, p in enumerate(proba)},
    }

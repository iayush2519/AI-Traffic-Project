"""
Full Data Pipeline: Raw CSV → Preprocessed & Feature-Engineered DataFrames.
Handles: missing values, normalization, outlier capping, time-based splits.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from ml.feature_engineering import build_features, get_feature_columns, NUMERIC_FEATURES

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "..", "models_trained")

# ── Time-based split ratios ────────────────────────────────────────────────────
TRAIN_FRAC = 0.70
VAL_FRAC   = 0.15
# TEST_FRAC  = 0.15  (remainder)


def load_raw(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = os.path.join(DATA_DIR, "raw_traffic_data.csv")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    print(f"[Pipeline] Loaded {len(df):,} rows from {path}")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill then back-fill numeric columns per intersection."""
    df = df.sort_values(["intersection_id", "timestamp"])
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df[numeric_cols] = (
        df.groupby("intersection_id")[numeric_cols]
        .transform(lambda x: x.ffill().bfill())
    )
    # Any remaining NaN (start of series) → column median
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    print(f"[Pipeline] Missing values handled. NaN count: {df.isna().sum().sum()}")
    return df


def cap_outliers(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """IQR-based outlier capping."""
    df = df.copy()
    for col in cols:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.01), df[col].quantile(0.99)
        df[col] = df[col].clip(lower=q1, upper=q3)
    return df


def normalize(df: pd.DataFrame, feature_cols: list[str], fit: bool = True,
              scaler_path: str | None = None) -> tuple[pd.DataFrame, StandardScaler]:
    scaler_path = scaler_path or os.path.join(MODEL_DIR, "scaler.pkl")
    os.makedirs(MODEL_DIR, exist_ok=True)

    valid_cols = [c for c in feature_cols if c in df.columns and df[c].dtype in [np.float64, np.int64, float, int]]

    if fit:
        scaler = StandardScaler()
        df[valid_cols] = scaler.fit_transform(df[valid_cols])
        joblib.dump(scaler, scaler_path)
        print(f"[Pipeline] Scaler fitted & saved → {scaler_path}")
    else:
        scaler = joblib.load(scaler_path)
        df[valid_cols] = scaler.transform(df[valid_cols])
        print(f"[Pipeline] Scaler loaded from {scaler_path}")
    return df, scaler


def time_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Time-aware split (no shuffling); based on global timestamp ordering."""
    df = df.sort_values("timestamp").reset_index(drop=True)
    n = len(df)
    train_end = int(n * TRAIN_FRAC)
    val_end   = int(n * (TRAIN_FRAC + VAL_FRAC))

    train = df.iloc[:train_end].copy()
    val   = df.iloc[train_end:val_end].copy()
    test  = df.iloc[val_end:].copy()

    print(f"[Pipeline] Split → train={len(train):,}  val={len(val):,}  test={len(test):,}")
    return train, val, test


def run_pipeline(raw_path: str | None = None) -> dict:
    """Full preprocessing → feature engineering → split → normalize."""
    df = load_raw(raw_path)
    df = handle_missing(df)
    df = cap_outliers(df, NUMERIC_FEATURES)

    # Feature engineering
    df = build_features(df)

    # Drop rows with NaN from lag features (first N rows per sensor)
    df = df.dropna().reset_index(drop=True)
    print(f"[Pipeline] After feature engineering & dropna: {len(df):,} rows")

    feature_cols = get_feature_columns(df)

    # Remove bool columns from normalization (they're already 0/1)
    num_feature_cols = [c for c in feature_cols
                        if df[c].dtype in [np.float64, np.int64]]

    train, val, test = time_split(df)

    # Normalize using train stats only
    train, scaler = normalize(train, num_feature_cols, fit=True)
    val, _        = normalize(val,   num_feature_cols, fit=False)
    test, _       = normalize(test,  num_feature_cols, fit=False)

    # Save processed splits
    os.makedirs(DATA_DIR, exist_ok=True)
    train.to_csv(os.path.join(DATA_DIR, "train.csv"), index=False)
    val.to_csv(os.path.join(DATA_DIR, "val.csv"),     index=False)
    test.to_csv(os.path.join(DATA_DIR, "test.csv"),   index=False)
    print("[Pipeline] Processed CSVs saved.")

    return {
        "train": train, "val": val, "test": test,
        "feature_cols": feature_cols,
        "num_feature_cols": num_feature_cols,
        "scaler": scaler,
    }


if __name__ == "__main__":
    from ml.synthetic_data_gen import generate_traffic_data
    generate_traffic_data(output_dir=DATA_DIR)
    run_pipeline()

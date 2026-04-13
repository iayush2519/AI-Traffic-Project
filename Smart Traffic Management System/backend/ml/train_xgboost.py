"""
XGBoost Congestion Classifier
Trains multi-class classifier for 5/15/30-minute horizon prediction.
"""

import os, json
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score, classification_report, roc_auc_score
)
from ml.feature_engineering import get_feature_columns, LABEL_MAP

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_trained")
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(MODEL_DIR, exist_ok=True)

TARGET_COL = "congestion_class"

# Horizon → number of 5-min steps to shift target forward
HORIZONS = {
    "5min":  1,
    "15min": 3,
    "30min": 6,
}


def load_split(split: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"{split}.csv")
    return pd.read_csv(path)


def prepare_horizon(df: pd.DataFrame, feature_cols: list[str], horizon_steps: int):
    """Shift target forward by horizon_steps per intersection."""
    df = df.sort_values(["intersection_id", "timestamp"]).copy()
    df["target"] = df.groupby("intersection_id")[TARGET_COL].shift(-horizon_steps)
    df = df.dropna(subset=["target"])
    df["target"] = df["target"].astype(int)

    valid_features = [c for c in feature_cols if c in df.columns]
    X = df[valid_features].values
    y = df["target"].values
    return X, y, valid_features


def train_xgboost(quick: bool = False) -> dict:
    print("[XGBoost] Loading data …")
    train_df = load_split("train")
    val_df   = load_split("val")
    test_df  = load_split("test")

    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    feature_cols = get_feature_columns(all_df)
    feature_cols = [c for c in feature_cols if c in train_df.columns]

    results = {}

    for horizon_name, horizon_steps in HORIZONS.items():
        print(f"\n[XGBoost] Training horizon={horizon_name} …")

        X_train, y_train, valid_feats = prepare_horizon(train_df, feature_cols, horizon_steps)
        X_val,   y_val,   _           = prepare_horizon(val_df,   feature_cols, horizon_steps)
        X_test,  y_test,  _           = prepare_horizon(test_df,  feature_cols, horizon_steps)

        if quick:
            param_grid = {"n_estimators": [100], "max_depth": [4], "learning_rate": [0.1]}
        else:
            param_grid = {
                "n_estimators": [100, 200],
                "max_depth":    [4, 6],
                "learning_rate":[0.05, 0.10],
                "subsample":    [0.8],
            }

        base_model = XGBClassifier(
            objective="multi:softprob",
            num_class=4,
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1,
        )

        if quick or len(param_grid["n_estimators"]) == 1:
            model = XGBClassifier(
                objective="multi:softprob", num_class=4,
                eval_metric="mlogloss", use_label_encoder=False,
                n_estimators=100, max_depth=4, learning_rate=0.1,
                subsample=0.8, random_state=42, n_jobs=-1,
            )
            model.fit(X_train, y_train,
                      eval_set=[(X_val, y_val)],
                      verbose=False)
        else:
            gs = GridSearchCV(base_model, param_grid, cv=3,
                              scoring="accuracy", n_jobs=-1, verbose=1)
            gs.fit(X_train, y_train)
            model = gs.best_estimator_
            print(f"[XGBoost] Best params: {gs.best_params_}")

        # Evaluate
        y_pred  = model.predict(X_test)
        y_proba = model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred,
                                       target_names=["low","medium","high","severe"],
                                       output_dict=True)
        try:
            auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")
        except Exception:
            auc = None

        print(f"[XGBoost] {horizon_name} → Acc={acc:.4f}  AUC={auc:.4f if auc else 'N/A'}")

        # Save model
        model_path = os.path.join(MODEL_DIR, f"xgboost_{horizon_name}.pkl")
        joblib.dump({"model": model, "features": valid_feats}, model_path)

        # Feature importance (top 20)
        fi = pd.Series(model.feature_importances_, index=valid_feats).nlargest(20)

        results[horizon_name] = {
            "accuracy": float(acc),
            "roc_auc": float(auc) if auc else None,
            "classification_report": report,
            "feature_importance": fi.to_dict(),
            "model_path": model_path,
        }

    # Save results JSON
    results_path = os.path.join(MODEL_DIR, "xgboost_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[XGBoost] Results saved → {results_path}")
    return results


def load_model(horizon: str = "15min"):
    path = os.path.join(MODEL_DIR, f"xgboost_{horizon}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"XGBoost model not found: {path}  — run /train_model first")
    return joblib.load(path)


if __name__ == "__main__":
    train_xgboost()

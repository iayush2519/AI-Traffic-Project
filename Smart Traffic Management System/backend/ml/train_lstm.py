"""
LSTM Congestion Predictor
Bidirectional LSTM with multi-horizon output heads (5/15/30 min).
"""

import os, json
import numpy as np
import pandas as pd
import joblib
from ml.feature_engineering import get_feature_columns, LABEL_MAP

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_trained")
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(MODEL_DIR, exist_ok=True)

SEQ_LEN    = 12   # 12 × 5 min = 60 min of history
NUM_CLASSES = 4
HORIZONS   = {"5min": 1, "15min": 3, "30min": 6}
BATCH_SIZE = 256
EPOCHS     = 30
PATIENCE   = 5


def build_sequences(df: pd.DataFrame, feature_cols: list[str],
                    seq_len: int, horizon_steps: int):
    """Build (N, seq_len, n_features) sequences per intersection."""
    df = df.sort_values(["intersection_id", "timestamp"]).copy()
    df["target"] = df.groupby("intersection_id")["congestion_class"].shift(-horizon_steps)
    df = df.dropna(subset=["target"])
    df["target"] = df["target"].astype(int)

    valid_feats = [c for c in feature_cols if c in df.columns]
    X_list, y_list = [], []

    for _, grp in df.groupby("intersection_id"):
        data = grp[valid_feats].values
        targets = grp["target"].values
        n = len(data)
        for i in range(seq_len, n):
            X_list.append(data[i - seq_len:i])
            y_list.append(targets[i])

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    return X, y, valid_feats


def build_lstm_model(seq_len: int, n_features: int, num_classes: int):
    """Build Bidirectional LSTM model."""
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models   # type: ignore
    except ImportError:
        raise ImportError("TensorFlow not installed. Run: uv pip install tensorflow")

    inp = layers.Input(shape=(seq_len, n_features))
    x   = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(inp)
    x   = layers.Dropout(0.3)(x)
    x   = layers.Bidirectional(layers.LSTM(64))(x)
    x   = layers.Dropout(0.2)(x)
    x   = layers.Dense(64, activation="relu")(x)
    out = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs=inp, outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_lstm() -> dict:
    try:
        import tensorflow as tf
        from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint  # type: ignore
        print(f"[LSTM] TensorFlow {tf.__version__}")
    except ImportError:
        print("[LSTM] TensorFlow not available — skipping LSTM training")
        return {}

    train_df = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    val_df   = pd.read_csv(os.path.join(DATA_DIR, "val.csv"))
    test_df  = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    all_df   = pd.concat([train_df, val_df, test_df])
    feature_cols = get_feature_columns(all_df)

    results = {}

    for horizon_name, horizon_steps in HORIZONS.items():
        print(f"\n[LSTM] Training horizon={horizon_name} …")

        X_tr, y_tr, feats = build_sequences(train_df, feature_cols, SEQ_LEN, horizon_steps)
        X_v,  y_v,  _     = build_sequences(val_df,   feature_cols, SEQ_LEN, horizon_steps)
        X_te, y_te, _     = build_sequences(test_df,  feature_cols, SEQ_LEN, horizon_steps)

        print(f"[LSTM] X_train={X_tr.shape}  X_val={X_v.shape}  X_test={X_te.shape}")

        n_features = X_tr.shape[2]
        model = build_lstm_model(SEQ_LEN, n_features, NUM_CLASSES)

        ckpt_path = os.path.join(MODEL_DIR, f"lstm_{horizon_name}.keras")
        callbacks = [
            EarlyStopping(monitor="val_loss", patience=PATIENCE, restore_best_weights=True),
            ModelCheckpoint(ckpt_path, save_best_only=True, monitor="val_loss"),
        ]

        history = model.fit(
            X_tr, y_tr,
            validation_data=(X_v, y_v),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=1,
        )

        # Evaluate
        loss, acc = model.evaluate(X_te, y_te, verbose=0)
        y_pred   = model.predict(X_te, verbose=0).argmax(axis=1)

        from sklearn.metrics import classification_report, roc_auc_score
        report = classification_report(y_te, y_pred,
                                       target_names=["low","medium","high","severe"],
                                       output_dict=True)
        proba  = model.predict(X_te, verbose=0)
        try:
            auc = roc_auc_score(y_te, proba, multi_class="ovr", average="macro")
        except Exception:
            auc = None

        print(f"[LSTM] {horizon_name} → Acc={acc:.4f}  AUC={auc:.4f if auc else 'N/A'}")

        # Save feature list
        meta_path = os.path.join(MODEL_DIR, f"lstm_{horizon_name}_meta.pkl")
        joblib.dump({"features": feats, "seq_len": SEQ_LEN}, meta_path)

        results[horizon_name] = {
            "accuracy": float(acc),
            "roc_auc": float(auc) if auc else None,
            "classification_report": report,
            "history": {
                "loss": [float(v) for v in history.history["loss"]],
                "val_loss": [float(v) for v in history.history["val_loss"]],
                "accuracy": [float(v) for v in history.history["accuracy"]],
                "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
            },
            "model_path": ckpt_path,
        }

    results_path = os.path.join(MODEL_DIR, "lstm_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[LSTM] Results saved → {results_path}")
    return results


def load_model(horizon: str = "15min"):
    try:
        import tensorflow as tf
    except ImportError:
        return None
    path = os.path.join(MODEL_DIR, f"lstm_{horizon}.keras")
    if not os.path.exists(path):
        return None
    model = tf.keras.models.load_model(path)
    meta  = joblib.load(os.path.join(MODEL_DIR, f"lstm_{horizon}_meta.pkl"))
    return {"model": model, "features": meta["features"], "seq_len": meta["seq_len"]}


if __name__ == "__main__":
    train_lstm()

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_DIR = "model"

MERCHANT_MODEL_PATH = os.path.join(MODEL_DIR, "merchant_model.pkl")
FRAUD_MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.pkl")


# ===============================
# MERCHANT RISK MODEL
# ===============================

def train_merchant_model(X, y):
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=150,
            random_state=42
        ))
    ])

    pipeline.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MERCHANT_MODEL_PATH)

    return pipeline


def load_merchant_model():
    if os.path.exists(MERCHANT_MODEL_PATH):
        return joblib.load(MERCHANT_MODEL_PATH)
    return None


# ===============================
# FRAUD MODEL (Self-learning)
# ===============================

def train_fraud_model(X):
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", IsolationForest(
            n_estimators=200,
            contamination=0.05,
            max_samples="auto",
            random_state=42
        ))
    ])

    pipeline.fit(X)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, FRAUD_MODEL_PATH)

    return pipeline


def load_fraud_model():
    if os.path.exists(FRAUD_MODEL_PATH):
        return joblib.load(FRAUD_MODEL_PATH)
    return None
# AI Service (Model-Focused)

This service provides AI-powered risk scoring, anomaly detection, realtime alerts, and dashboard analytics for the rental platform.

## Main Ideas

1. Learn risk directly from booking behavior in MongoDB.
2. Keep models in memory for fast inference and persist to disk with joblib.
3. Retrain automatically on a schedule to adapt to new behavior.
4. Combine model outputs with rule-based safeguards for explainable alerts.
5. Expose everything through FastAPI endpoints plus a WebSocket alert stream.

## Models Used (Current Runtime)

The active runtime models are defined in [services/model_manager.py](services/model_manager.py):

1. Merchant Risk Model
- Type: `RandomForestClassifier`
- Pipeline: `StandardScaler` -> `RandomForestClassifier(n_estimators=150, random_state=42)`
- Storage: `model/merchant_model.pkl`
- Target label: generated during feature extraction as:
	- `1` (risky) if cancellation rate > 0.5 OR recent cancellation rate > 0.5
	- `0` otherwise

2. Fraud Detection Model
- Type: `IsolationForest` (unsupervised anomaly detection)
- Pipeline: `StandardScaler` -> `IsolationForest(n_estimators=200, contamination=0.05, random_state=42)`
- Storage: `model/fraud_model.pkl`
- Predicts anomalies (`-1`) and uses decision score as `riskScore`.

## Feature Engineering

### Merchant Features
Implemented in [services/merchant_scoring.py](services/merchant_scoring.py):

- total bookings
- acceptance rate
- cancellation rate
- recent (last 30 days) cancellation rate
- booking frequency per week
- days since last booking

Risk levels are mapped from probability:
- `HIGH` >= 0.8
- `MEDIUM` >= 0.5
- `LOW` < 0.5

### Fraud Features
Implemented in [services/fraud_detection.py](services/fraud_detection.py):

- total bookings
- cancelled bookings
- confirmed bookings
- confirmed rate
- cancellation rate
- recent (last 30 days) cancellation rate
- booking frequency per month
- days since last booking

Fraud case detection combines model output + business rules:
- anomaly prediction (`IsolationForest` predicts `-1`), or
- cancellation rate > 0.75, or
- recent cancellation rate > 0.6

## Retraining Strategy

Automatic retraining is implemented in [services/scheduler/auto_retrain.py](services/scheduler/auto_retrain.py):

- Retrains both fraud and merchant models
- Auto-blocks high-risk merchants after scoring
- Refreshes analytics
- Runs every 21600 seconds (6 hours)

Manual retraining endpoints in [main.py](main.py):
- `POST /retrain/merchant`
- `POST /retrain/fraud`

## API Surface (High-Level)

Defined in [main.py](main.py):

- `GET /health`
- `GET /merchant-risk`
- `GET /fraud-detection`
- `GET /analytics`
- `GET /alerts`
- `POST /block-risky-merchants`
- `POST /retrain/merchant`
- `POST /retrain/fraud`
- `WS /ws/alerts` (pushes alert payload every 5 seconds)

## Data Sources

MongoDB collections used:
- `users`
- `bookings`

Connection is loaded from `.env`:
- `MONGO_URI`
- `DB_NAME`

## Run Locally

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Create `.env`

```env
MONGO_URI=your_mongo_connection_string
DB_NAME=your_database_name
```

3. Start API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Important Note

There are older standalone training scripts in [services/train_merchant_model.py](services/train_merchant_model.py) and [services/train_fraud_model.py](services/train_fraud_model.py).

Those scripts are not the active runtime path used by the API endpoints. The runtime models come from the pipelines in [services/model_manager.py](services/model_manager.py) and are fed by live MongoDB feature extraction.

from fastapi import FastAPI
import asyncio

from services.merchant_scoring import calculate_merchant_risk_from_db, retrain_merchant_model
from services.fraud_detection import detect_fraud_from_db, retrain_fraud_model
from services.analytics import system_analytics_from_db
from services.scheduler.auto_retrain import auto_retrain  # ← fixed import

app = FastAPI(title="AI Service Dashboard")


@app.on_event("startup")
async def start_scheduler():
    print("🚀 Starting AI auto-retraining scheduler...")
    asyncio.create_task(auto_retrain())


# Merchant risk
@app.get("/merchant-risk")
async def merchant_risk():
    results = await calculate_merchant_risk_from_db()
    return {"merchantRisk": results}


# Fraud detection
@app.get("/fraud-detection")
async def fraud_detection():
    results = await detect_fraud_from_db()
    return results


# System analytics
@app.get("/analytics")
async def analytics():
    results = await system_analytics_from_db()
    return results


# Manual retraining
@app.post("/retrain/merchant")
async def retrain_merchant():
    await retrain_merchant_model()
    return {"status": "Merchant model retrained"}


@app.post("/retrain/fraud")
async def retrain_fraud():
    await retrain_fraud_model()
    return {"status": "Fraud model retrained"}
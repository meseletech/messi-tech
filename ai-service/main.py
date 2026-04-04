from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import traceback

from services.merchant_scoring import (
    calculate_merchant_risk_from_db,
    retrain_merchant_model,
    auto_block_risky_merchants,
)
from services.fraud_detection import detect_fraud_from_db, retrain_fraud_model
from services.analytics import system_analytics_from_db, get_realtime_alerts
from services.scheduler.auto_retrain import auto_retrain

# ==========================
# Initialize FastAPI
# ==========================
app = FastAPI(title="AI Service Dashboard")

# ==========================
# CORS configuration
# ==========================
origins = [
    "http://localhost:5173",               # Vue dev server
    "https://messi-tech-q223.vercel.app", # Production frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Startup event: auto-retrain scheduler
# ==========================
@app.on_event("startup")
async def start_scheduler():
    print("🚀 Starting AI auto-retraining scheduler...")
    asyncio.create_task(auto_retrain())

# ==========================
# Health check
# ==========================
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}

# ==========================
# Merchant risk
# ==========================
@app.get("/merchant-risk")
async def merchant_risk():
    try:
        results = await calculate_merchant_risk_from_db()
        return {"merchantRisk": results}
    except Exception as e:
        print("❌ Error in /merchant-risk endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# Fraud detection
# ==========================
@app.get("/fraud-detection")
async def fraud_detection():
    try:
        results = await detect_fraud_from_db()
        return results
    except Exception as e:
        print("❌ Error in /fraud-detection endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# System analytics
# ==========================
@app.get("/analytics")
async def analytics():
    try:
        results = await system_analytics_from_db()
        return results
    except Exception as e:
        print("❌ Error in /analytics endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# Real-time AI alerts
# ==========================
@app.get("/alerts")
async def alerts():
    try:
        results = await get_realtime_alerts()
        return results
    except Exception as e:
        print("❌ Error in /alerts endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                alert_payload = await get_realtime_alerts()
                await websocket.send_json(alert_payload)
            except Exception as e:
                print("❌ Error sending websocket alert:")
                print(traceback.format_exc())
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

# ==========================
# Risk mitigation
# ==========================
@app.post("/block-risky-merchants")
async def block_risky_merchants():
    try:
        result = await auto_block_risky_merchants()
        return result
    except Exception as e:
        print("❌ Error in /block-risky-merchants endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# Manual retraining endpoints
# ==========================
@app.post("/retrain/merchant")
async def retrain_merchant():
    try:
        await retrain_merchant_model()
        return {"status": "Merchant model retrained"}
    except Exception as e:
        print("❌ Error in /retrain/merchant endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrain/fraud")
async def retrain_fraud():
    try:
        await retrain_fraud_model()
        return {"status": "Fraud model retrained"}
    except Exception as e:
        print("❌ Error in /retrain/fraud endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
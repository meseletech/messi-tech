from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from services.merchant_scoring import calculate_merchant_risk_from_db, retrain_merchant_model
from services.fraud_detection import detect_fraud_from_db, retrain_fraud_model
from services.analytics import system_analytics_from_db
from services.scheduler.auto_retrain import auto_retrain

# ==========================
# Initialize FastAPI
# ==========================
app = FastAPI(title="AI Service Dashboard")

# ==========================
# CORS configuration
# ==========================
origins = [
    "http://localhost:5173",            # Vue dev server
    "https://messi-tech-q223.vercel.app", # Production frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # Allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
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
    results = await calculate_merchant_risk_from_db()
    return {"merchantRisk": results}

# ==========================
# Fraud detection
# ==========================
@app.get("/fraud-detection")
async def fraud_detection():
    results = await detect_fraud_from_db()
    return results

# ==========================
# System analytics
# ==========================
@app.get("/analytics")
async def analytics():
    results = await system_analytics_from_db()
    return results

# ==========================
# Manual retraining endpoints
# ==========================
@app.post("/retrain/merchant")
async def retrain_merchant():
    await retrain_merchant_model()
    return {"status": "Merchant model retrained"}

@app.post("/retrain/fraud")
async def retrain_fraud():
    await retrain_fraud_model()
    return {"status": "Fraud model retrained"}
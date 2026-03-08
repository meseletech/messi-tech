import os
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from services.model_manager import train_merchant_model, load_merchant_model

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

merchants_collection = db["users"]
bookings_collection = db["bookings"]

# global model variable
merchant_model = load_merchant_model()

async def extract_merchant_features():
    merchants_cursor = merchants_collection.find({"role": "merchant"})

    X = []
    y = []
    merchant_map = []

    async for merchant in merchants_cursor:
        booking_filter = {"merchant": merchant["_id"]}

        total = await bookings_collection.count_documents(booking_filter)
        accepted = await bookings_collection.count_documents({
            **booking_filter,
            "status": {"$in": ["ACCEPTED", "CONFIRMED"]}
        })
        cancelled = await bookings_collection.count_documents({
            **booking_filter,
            "status": "CANCELLED"
        })

        acceptance_rate = accepted / total if total > 0 else 0
        cancellation_rate = cancelled / total if total > 0 else 0

        features = [total, acceptance_rate, cancellation_rate]

        X.append(features)
        merchant_map.append(merchant)

        y.append(1 if cancellation_rate > 0.5 else 0)

    return np.array(X), np.array(y), merchant_map


async def retrain_merchant_model():
    global merchant_model
    X, y, _ = await extract_merchant_features()
    if len(X) > 0:
        merchant_model = train_merchant_model(X, y)
        print("✅ Merchant model updated in memory and saved")


async def calculate_merchant_risk_from_db():
    global merchant_model
    X, y, merchant_map = await extract_merchant_features()
    if len(X) == 0:
        return []

    if merchant_model is None:
        merchant_model = train_merchant_model(X, y)

    predictions = merchant_model.predict(X)

    results = []
    for i, pred in enumerate(predictions):
        risk_level = "HIGH" if pred == 1 else "LOW"
        results.append({
            "merchantId": str(merchant_map[i]["_id"]),
            "features": X[i].tolist(),
            "riskLevel": risk_level
        })

    return results
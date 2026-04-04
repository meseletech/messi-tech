import os
import numpy as np
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from services.model_manager import train_merchant_model, load_merchant_model

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

merchants_collection = db["users"]
bookings_collection = db["bookings"]

merchant_model = load_merchant_model()


def _risk_level_from_probability(probability):
    if probability >= 0.8:
        return "HIGH"
    if probability >= 0.5:
        return "MEDIUM"
    return "LOW"


def _id_from_string(merchant_id):
    try:
        from bson import ObjectId
        return ObjectId(merchant_id)
    except Exception:
        return merchant_id

async def extract_merchant_features():
    merchants_cursor = merchants_collection.find({"role": "merchant"})

    X = []
    y = []
    merchant_map = []
    now = datetime.utcnow()
    thirty_days = now - timedelta(days=30)

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
        recent_total = await bookings_collection.count_documents({
            **booking_filter,
            "createdAt": {"$gte": thirty_days}
        })
        recent_cancelled = await bookings_collection.count_documents({
            **booking_filter,
            "createdAt": {"$gte": thirty_days},
            "status": "CANCELLED"
        })

        acceptance_rate = accepted / total if total > 0 else 0
        cancellation_rate = cancelled / total if total > 0 else 0
        recent_cancellation_rate = recent_cancelled / recent_total if recent_total > 0 else 0

        latest_booking = await bookings_collection.find_one(booking_filter, sort=[("createdAt", -1)])
        earliest_booking = await bookings_collection.find_one(booking_filter, sort=[("createdAt", 1)])

        if latest_booking and latest_booking.get("createdAt"):
            days_since_last = (now - latest_booking["createdAt"]).days
        else:
            days_since_last = 999

        if earliest_booking and earliest_booking.get("createdAt") and latest_booking and latest_booking.get("createdAt"):
            history_days = max((latest_booking["createdAt"] - earliest_booking["createdAt"]).days, 1)
        else:
            history_days = 1

        frequency_per_week = total / max(history_days / 7, 1)

        features = [
            total,
            acceptance_rate,
            cancellation_rate,
            recent_cancellation_rate,
            frequency_per_week,
            days_since_last
        ]

        X.append(features)
        merchant_map.append(merchant)
        y.append(1 if cancellation_rate > 0.5 or recent_cancellation_rate > 0.5 else 0)

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

    probabilities = np.zeros(len(X), dtype=float)
    if hasattr(merchant_model, "predict_proba"):
        proba = merchant_model.predict_proba(X)
        if proba.ndim == 2:
            if proba.shape[1] == 1:
                model_classes = merchant_model.named_steps["model"].classes_
                if len(model_classes) == 1 and model_classes[0] == 1:
                    probabilities = proba[:, 0]
                else:
                    probabilities = 1.0 - proba[:, 0]
            else:
                model_classes = merchant_model.named_steps["model"].classes_
                if 1 in model_classes:
                    idx = list(model_classes).index(1)
                else:
                    idx = 0
                probabilities = proba[:, idx]
        else:
            probabilities = proba.flatten()

    results = []
    for i, prob in enumerate(probabilities):
        risk_level = _risk_level_from_probability(prob)
        results.append({
            "merchantId": str(merchant_map[i]["_id"]),
            "features": X[i].tolist(),
            "riskLevel": risk_level,
            "riskProbability": float(round(prob, 4)),
            "suggestedAction": "block" if risk_level == "HIGH" else "review"
        })

    return results


async def auto_block_risky_merchants(threshold: float = 0.8):
    merchant_risks = await calculate_merchant_risk_from_db()
    blocked_merchants = []

    for risk in merchant_risks:
        if risk["riskProbability"] >= threshold and risk["riskLevel"] == "HIGH":
            merchant_id = risk["merchantId"]
            update_result = await merchants_collection.update_one(
                {"_id": _id_from_string(merchant_id)},
                {
                    "$set": {
                        "isBlocked": True,
                        "blockedAt": datetime.utcnow(),
                        "blockedReason": "High AI risk score"
                    }
                }
            )
            if update_result.modified_count > 0:
                blocked_merchants.append(merchant_id)

    return {
        "blockedCount": len(blocked_merchants),
        "blockedMerchants": blocked_merchants,
        "threshold": threshold
    }
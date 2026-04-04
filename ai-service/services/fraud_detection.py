import os
import numpy as np
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from services.model_manager import train_fraud_model, load_fraud_model

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

users_collection = db["users"]
bookings_collection = db["bookings"]

# Global model variable (keeps model in memory)
fraud_model = load_fraud_model()


async def extract_features():
    users_cursor = users_collection.find({
        "role": {"$in": ["customer", "merchant"]}
    })

    feature_data = []
    user_map = []
    now = datetime.utcnow()
    thirty_days = now - timedelta(days=30)

    async for user in users_cursor:

        booking_filter = {}
        if user["role"] == "customer":
            booking_filter["customer"] = user["_id"]
        else:
            booking_filter["merchant"] = user["_id"]

        total = await bookings_collection.count_documents(booking_filter)

        cancelled_filter = booking_filter.copy()
        cancelled_filter["status"] = "CANCELLED"
        cancelled = await bookings_collection.count_documents(cancelled_filter)

        confirmed_filter = booking_filter.copy()
        confirmed_filter["status"] = {"$in": ["CONFIRMED", "ACCEPTED"]}
        confirmed = await bookings_collection.count_documents(confirmed_filter)

        recent_total = await bookings_collection.count_documents({
            **booking_filter,
            "createdAt": {"$gte": thirty_days}
        })
        recent_cancelled = await bookings_collection.count_documents({
            **booking_filter,
            "createdAt": {"$gte": thirty_days},
            "status": "CANCELLED"
        })

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

        rate = cancelled / total if total > 0 else 0
        confirmed_rate = confirmed / total if total > 0 else 0
        recent_cancellation_rate = recent_cancelled / recent_total if recent_total > 0 else 0
        frequency_per_month = total / max(history_days / 30, 1)

        feature_data.append([
            total,
            cancelled,
            confirmed,
            confirmed_rate,
            rate,
            recent_cancellation_rate,
            frequency_per_month,
            days_since_last
        ])
        user_map.append(user)

    return np.array(feature_data), user_map


async def retrain_fraud_model():
    global fraud_model

    X, _ = await extract_features()

    if len(X) > 0:
        fraud_model = train_fraud_model(X)
        print("✅ Fraud model updated in memory and saved")


async def detect_fraud_from_db():
    global fraud_model

    X, user_map = await extract_features()

    if len(X) == 0:
        return {
            "checkedUsers": 0,
            "fraudCases": [],
            "totalFrauds": 0
        }

    if fraud_model is None:
        fraud_model = train_fraud_model(X)

    predictions = fraud_model.predict(X)
    scores = fraud_model.decision_function(X) if hasattr(fraud_model, "decision_function") else np.zeros(len(X))

    fraud_cases = []

    for i, pred in enumerate(predictions):
        total = int(X[i][0])
        cancelled = int(X[i][1])
        confirmed = int(X[i][2])
        confirmed_rate = float(X[i][3])
        rate = float(X[i][4])
        recent_cancellation_rate = float(X[i][5])
        frequency_per_month = float(X[i][6])
        days_since_last = int(X[i][7])

        is_fraud = pred == -1 or rate > 0.75 or recent_cancellation_rate > 0.6
        if not is_fraud:
            continue

        reason = "Anomalous booking patterns detected"
        if total == 0:
            reason = "No booking activity"
        elif rate > 0.75:
            reason = "High cancellation rate"
        elif recent_cancellation_rate > 0.6:
            reason = "Recent cancellation spike"
        elif days_since_last < 2 and total > 8:
            reason = "Fast repeated cancellation activity"

        fraud_cases.append({
            "userId": str(user_map[i]["_id"]),
            "role": user_map[i]["role"],
            "totalBookings": total,
            "cancelledBookings": cancelled,
            "confirmedBookings": confirmed,
            "confirmedRate": confirmed_rate,
            "cancellationRate": rate,
            "recentCancellationRate": recent_cancellation_rate,
            "frequencyPerMonth": round(frequency_per_month, 2),
            "daysSinceLastBooking": days_since_last,
            "riskScore": float(round(float(scores[i]), 4)),
            "riskReason": reason
        })

    return {
        "checkedUsers": len(user_map),
        "fraudCases": fraud_cases,
        "totalFrauds": len(fraud_cases)
    }
import os
import numpy as np
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

        rate = cancelled / total if total > 0 else 0

        feature_data.append([total, cancelled, confirmed, rate])
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

    fraud_cases = []

    for i, pred in enumerate(predictions):

        if pred == -1:  # anomaly detected

            total = int(X[i][0])
            cancelled = int(X[i][1])
            confirmed = int(X[i][2])
            rate = float(X[i][3])

            # AI explanation logic
            reason = "Abnormal activity detected"

            if rate > 0.7:
                reason = "High cancellation rate"

            elif cancelled > 5:
                reason = "Too many cancelled bookings"

            elif total == 0:
                reason = "No booking activity"

            fraud_cases.append({
                "userId": str(user_map[i]["_id"]),
                "role": user_map[i]["role"],
                "totalBookings": total,
                "cancelledBookings": cancelled,
                "confirmedBookings": confirmed,
                "cancellationRate": rate,
                "riskReason": reason
            })

    return {
        "checkedUsers": len(user_map),
        "fraudCases": fraud_cases,
        "totalFrauds": len(fraud_cases)
    }
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

users_collection = db["users"]
bookings_collection = db["bookings"]

async def system_analytics_from_db():
    total_customers = await users_collection.count_documents({"role": "customer"})
    total_merchants = await users_collection.count_documents({"role": "merchant"})
    total_bookings = await bookings_collection.count_documents({})
    peak_cursor = bookings_collection.aggregate([
        {"$group": {"_id": {"$hour": "$createdAt"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ])
    peak_data = await peak_cursor.to_list(length=1)
    peak_hour = peak_data[0]["_id"] if peak_data else None

    analytics = {
        "totalCustomers": total_customers,
        "totalMerchants": total_merchants,
        "totalBookings": total_bookings,
        "peakBookingHour": peak_hour
    }

    print("📊 Updated System Analytics:", analytics)
    return analytics


async def get_realtime_alerts(limit: int = 10):
    from services.fraud_detection import detect_fraud_from_db
    from services.merchant_scoring import calculate_merchant_risk_from_db

    merchant_risks = await calculate_merchant_risk_from_db()
    fraud_data = await detect_fraud_from_db()

    high_risk_merchants = [m for m in merchant_risks if m["riskLevel"] == "HIGH"]
    high_risk_merchants = sorted(high_risk_merchants, key=lambda item: item["riskProbability"], reverse=True)[:limit]

    alert_items = []
    for merchant in high_risk_merchants:
        alert_items.append({
            "type": "merchantRisk",
            "merchantId": merchant["merchantId"],
            "riskLevel": merchant["riskLevel"],
            "riskProbability": merchant["riskProbability"],
            "message": f"Merchant {merchant['merchantId']} flagged as HIGH risk."
        })

    for fraud_case in fraud_data.get("fraudCases", [])[:limit]:
        alert_items.append({
            "type": "fraudAlert",
            "userId": fraud_case["userId"],
            "role": fraud_case["role"],
            "riskReason": fraud_case["riskReason"],
            "riskScore": fraud_case["riskScore"],
            "message": f"{fraud_case['role'].title()} {fraud_case['userId']} flagged for {fraud_case['riskReason']}."
        })

    return {
        "alerts": alert_items,
        "merchantRiskCount": len(high_risk_merchants),
        "fraudAlertCount": len(fraud_data.get("fraudCases", []))
    }
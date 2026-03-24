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
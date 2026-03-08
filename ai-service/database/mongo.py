from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["leasing_ai"]

# ✅ DEFINE ALL COLLECTIONS USED IN SERVICES
bookings_collection = db["bookings"]
merchants_collection = db["merchants"]

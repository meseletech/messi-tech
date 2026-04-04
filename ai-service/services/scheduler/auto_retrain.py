import asyncio
from services.analytics import system_analytics_from_db
from services.fraud_detection import retrain_fraud_model
from services.merchant_scoring import retrain_merchant_model, auto_block_risky_merchants


async def auto_retrain():
    while True:
        try:
            print("🔄 Retraining AI models...")

            # Retrain AI models
            await retrain_fraud_model()
            print("✅ Fraud model updated")

            await retrain_merchant_model()
            print("✅ Merchant model updated")

            # Auto-block risky merchants after retraining
            block_result = await auto_block_risky_merchants()
            print(f"🔐 Auto-blocked {block_result['blockedCount']} risky merchants")

            # Run analytics
            analytics = await system_analytics_from_db()

            print("📊 Updated System Analytics:")
            print(analytics)

        except Exception as e:
            print("❌ Scheduler error:", e)

        await asyncio.sleep(21600)  
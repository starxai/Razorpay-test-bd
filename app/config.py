import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

db_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))


db = db_client["razorpay_demo"]
wallet_collection = db["wallets"]
topup_collection = db["wallet_topups"]

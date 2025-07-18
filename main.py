from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.topup_wallet import RazorpayOrderRequest
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET, topup_collection
from app.services import topup_wallet, get_wallet_balance
from datetime import datetime
import razorpay
import hmac
import hashlib
import json

app = FastAPI()

origins = [
    "https://razorpay-payment-eight.vercel.app",
    "http://localhost:3000"
    ]  # Adjust for your React app
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.post("/create-order")
async def create_order(payload: RazorpayOrderRequest):
    try:
        amount_in_paise = int(payload.amount * 100)
        order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "user_id": payload.user_id
            }
        })
        return order
    except Exception as e:
        print(f"❌ Razorpay order creation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to create order", "details": str(e)}
        )

@app.post("/webhook")
async def razorpay_webhook(request: Request, x_razorpay_signature: str = Header(None)):
    body = await request.body()
    received_signature = x_razorpay_signature

    generated_signature = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if generated_signature != received_signature:
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = json.loads(body)
    event = data.get("event")
    payment = data.get("payload", {}).get("payment", {}).get("entity", {})
    
    if event == "payment.captured":
        user_id = payment["notes"].get("user_id")
        amount = float(payment["amount"]) / 100
        txn_id = payment["id"]

        print(amount)

        await topup_wallet(user_id, amount)

        await topup_collection.insert_one({
            "user_id": user_id,
            "amount": amount,
            "method": "razorpay",
            "txn_id": txn_id,
            "status": "success",
            "timestamp": datetime.utcnow()
        })

    return {"status": "ok"}

@app.get("/wallet/{user_id}")
async def check_wallet(user_id: str):
    balance = await get_wallet_balance(user_id)
    return {"user_id": user_id, "balance": balance}

@app.get("/test")
async def root():
    return {"message": "razorpay Backend Running"}

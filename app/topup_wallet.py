from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class CreditTopUp(BaseModel):
    user_id: str
    amount: float  # in INR
    txn_id: str  # Razorpay payment_id
    method: Literal["razorpay", "manual"]
    status: Literal["success", "failed"]
    timestamp: datetime

class RazorpayOrderRequest(BaseModel):
    amount: float  # INR
    user_id: str
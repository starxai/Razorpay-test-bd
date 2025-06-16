from pydantic import BaseModel
from datetime import datetime

class WalletRecord(BaseModel):
    user_id: str
    wallet_balance_inr: float = 0.0
    last_updated: datetime = datetime.utcnow()

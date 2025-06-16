from app.config import wallet_collection

async def topup_wallet(user_id: str, amount: float):
    await wallet_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

async def get_wallet_balance(user_id: str):
    doc = await wallet_collection.find_one({"user_id": user_id})
    return doc.get("balance", 0) if doc else 0

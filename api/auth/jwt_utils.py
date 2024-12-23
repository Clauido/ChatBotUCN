import jwt 
from fastapi import HTTPException, Request
from datetime import datetime, timezone, timedelta
from config import JWT_SECRET, JWT_DURATION

def generate_token(id: int, email: str) -> str:
    payload = {
        "id": id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_DURATION)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return f"Bearer {token}"

def verify_token(token: str) -> dict:
    return jwt.decode(token.split(" ")[1], JWT_SECRET, algorithms=["HS256"])    
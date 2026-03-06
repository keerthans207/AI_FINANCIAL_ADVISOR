# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Any

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class TransactionIn(BaseModel):
    date: str
    amount: float
    description: Optional[str] = None

class AdvisorRequest(BaseModel):
    user_id: int
    # optional override profile
    risk_profile: Optional[str] = "medium"
    preferred_summary_style: Optional[str] = "bullet"

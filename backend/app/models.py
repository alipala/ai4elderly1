# Backend: app/models.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime,date

class SpendingEntry(BaseModel):
    date: str
    category: str
    amount: float
    description: Optional[str] = None

class UserProfile(BaseModel):
    id: Optional[str] = None
    name: str
    age: Optional[int] = None
    income: Optional[float] = None
    savings: Optional[float] = None
    debts: Optional[float] = None
    investments: Optional[str] = None
    financial_goals: List[str] = []
    spending_data: List[dict] = []
    spending_data: List[SpendingEntry] = []
    conversation_history: List[dict] = []
    voice_features: Optional[List[float]] = None

class UserInput(BaseModel):
    message: str

class BotResponse(BaseModel):
    message: str
    sentiment: str
    confidence: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

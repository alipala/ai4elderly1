from dotenv import load_dotenv
load_dotenv()

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import uvicorn
import json
import uuid
from datetime import datetime, timedelta
import random
import re
from typing import List, Optional
import torch
from transformers import pipeline
from openai import OpenAI
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Financial Advisor API",
    description="API for AI-powered financial advice for elderly and visually impaired users",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize sentiment analysis pipeline
try:
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=device)
except Exception as e:
    logger.error(f"Error loading sentiment analysis model: {e}")
    logger.info("Falling back to a simpler sentiment analysis method.")
    sentiment_analyzer = None

# Define the path for storing user profiles (this will be replaced with MongoDB in the next step)
PROFILES_FOLDER = './financial_advisor_profiles'
if not os.path.exists(PROFILES_FOLDER):
    os.makedirs(PROFILES_FOLDER)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()


# Pydantic models
class UserProfile(BaseModel):
    id: str
    name: str
    age: Optional[int] = None
    income: Optional[float] = None
    savings: Optional[float] = None
    debts: Optional[float] = None
    investments: Optional[str] = None
    financial_goals: List[str] = []
    spending_data: List[dict] = []
    conversation_history: List[dict] = []

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

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Helper Functions

def generate_unique_id():
    """Generate a unique identifier for a user profile."""
    return str(uuid.uuid4())

def save_profile(profile: UserProfile):
    """Save a user profile to a JSON file."""
    filename = os.path.join(PROFILES_FOLDER, f"{profile.id}.json")
    with open(filename, 'w') as f:
        json.dump(profile.dict(), f)

def load_profile(profile_id: str) -> Optional[UserProfile]:
    """Load a user profile from a JSON file."""
    filename = os.path.join(PROFILES_FOLDER, f"{profile_id}.json")
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return UserProfile(**json.load(f))
    return None

def analyze_sentiment(text: str):
    """Analyze the sentiment of the given text."""
    if sentiment_analyzer:
        try:
            result = sentiment_analyzer(text)[0]
            return result['label'], result['score']
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")

    # Fallback simple sentiment analysis
    positive_words = set(['good', 'great', 'happy', 'positive', 'optimistic'])
    negative_words = set(['bad', 'terrible', 'sad', 'negative', 'worried', 'concerned'])
    
    words = text.lower().split()
    positive_count = sum(word in positive_words for word in words)
    negative_count = sum(word in negative_words for word in words)
    
    if positive_count > negative_count:
        return 'POSITIVE', 0.7
    elif negative_count > positive_count:
        return 'NEGATIVE', 0.7
    else:
        return 'NEUTRAL', 0.5

def get_financial_context(text: str):
    """Determine the financial context of the given text."""
    patterns = {
        'spending': r'\b(buy|purchase|spend)\b',
        'saving': r'\b(save|deposit)\b',
        'investment': r'\b(invest|stock|bond)\b',
        'debt': r'\b(debt|loan|borrow)\b',
        'income': r'\b(income|salary|pension)\b'
    }
    
    contexts = [context for context, pattern in patterns.items() if re.search(pattern, text, re.IGNORECASE)]
    return contexts if contexts else ['general']

def generate_ai_response(profile: UserProfile, user_input: str) -> str:
    """Generate an AI response based on the user's input and profile."""
    sentiment, confidence = analyze_sentiment(user_input)
    contexts = get_financial_context(user_input)
    
    prompt = f"The elderly client (Name: {profile.name}, Age: {profile.age}) said: '{user_input}'. "
    prompt += f"Their sentiment is {sentiment.lower()} (confidence: {confidence:.2f}). "
    prompt += f"The financial context is related to {', '.join(contexts)}. "
    prompt += f"\n\nUser's financial profile:\n"
    prompt += f"Income: {profile.income}, Savings: {profile.savings}, Debts: {profile.debts}\n"
    prompt += f"Investments: {profile.investments}\n"
    prompt += f"Financial goals: {', '.join(profile.financial_goals)}\n"
    prompt += "\nProvide an empathetic response and appropriate financial advice, "
    prompt += "considering their emotional state, financial context, and profile information."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=200,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return "I apologize, but I'm having trouble generating a response. Could we try again?"

# Security functions

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "disabled": False,
    }
}

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# API Endpoints

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/create_profile", response_model=UserProfile)
async def create_profile(profile: UserProfile, current_user: User = Depends(get_current_active_user)):
    """Create a new user profile."""
    profile.id = generate_unique_id()
    save_profile(profile)
    logger.info(f"Created new profile for user: {profile.name}")
    return profile

@app.get("/get_profile/{profile_id}", response_model=UserProfile)
async def get_profile(profile_id: str, current_user: User = Depends(get_current_active_user)):
    """Retrieve a user profile by ID."""
    profile = load_profile(profile_id)
    if not profile:
        logger.warning(f"Profile not found: {profile_id}")
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/update_profile/{profile_id}", response_model=UserProfile)
async def update_profile(profile_id: str, updated_profile: UserProfile, current_user: User = Depends(get_current_active_user)):
    """Update an existing user profile."""
    existing_profile = load_profile(profile_id)
    if not existing_profile:
        logger.warning(f"Profile not found for update: {profile_id}")
        raise HTTPException(status_code=404, detail="Profile not found")
    updated_profile.id = profile_id
    save_profile(updated_profile)
    logger.info(f"Updated profile for user: {updated_profile.name}")
    return updated_profile

@app.post("/chat/{profile_id}", response_model=BotResponse)
async def chat(profile_id: str, user_input: UserInput, current_user: User = Depends(get_current_active_user)):
    """Process user input and generate a bot response."""
    profile = load_profile(profile_id)
    if not profile:
        logger.warning(f"Profile not found for chat: {profile_id}")
        raise HTTPException(status_code=404, detail="Profile not found")
    
    ai_response = generate_ai_response(profile, user_input.message)
    sentiment, confidence = analyze_sentiment(user_input.message)
    
    # Update conversation history
    profile.conversation_history.append({
        "user": user_input.message,
        "bot": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    save_profile(profile)
    
    logger.info(f"Generated response for user: {profile.name}")
    return BotResponse(message=ai_response, sentiment=sentiment, confidence=confidence)

@app.get("/conversation_history/{profile_id}", response_model=List[dict])
async def get_conversation_history(profile_id: str, current_user: User = Depends(get_current_active_user)):
    """Retrieve the conversation history for a user."""
    profile = load_profile(profile_id)
    if not profile:
        logger.warning(f"Profile not found for conversation history: {profile_id}")
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.conversation_history

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
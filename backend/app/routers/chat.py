# Backend: app/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException
from app.models import UserInput, BotResponse
from app.services.ai_service import AIService
from app.services.profile_service import ProfileService
from app.dependencies import get_current_active_user
from datetime import datetime  # Add this import

router = APIRouter()

@router.post("/chat/{profile_id}", response_model=BotResponse)
async def chat(profile_id: str, user_input: UserInput, current_user: dict = Depends(get_current_active_user)):
    profile = await ProfileService.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    ai_response, sentiment, confidence = await AIService.process_user_input(profile, user_input)
    
    timestamp = datetime.now().isoformat()
    await ProfileService.save_conversation(profile_id, user_input.message, ai_response, timestamp)
    
    return BotResponse(message=ai_response, sentiment=sentiment, confidence=confidence)

@router.get("/conversation_history/{profile_id}")
async def get_conversation_history(profile_id: str, current_user: dict = Depends(get_current_active_user)):
    profile = await ProfileService.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.conversation_history

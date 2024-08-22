# Backend: app/services/ai_service.py
from app.models import UserProfile, UserInput
from app.services.openai_service import generate_ai_response
from app.services.sentiment_service import analyze_sentiment

class AIService:
    @staticmethod
    async def process_user_input(profile: UserProfile, user_input: UserInput):
        ai_response = generate_ai_response(profile, user_input.message)
        sentiment, confidence = analyze_sentiment(user_input.message)
        return ai_response, sentiment, confidence
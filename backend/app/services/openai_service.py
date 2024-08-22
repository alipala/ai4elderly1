# Backend: app/services/openai_service.py
from openai import OpenAI
from app.config import settings
from app.models import UserProfile

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_ai_response(profile: UserProfile, user_input: str) -> str:
    prompt = f"The elderly client (Name: {profile.name}, Age: {profile.age}) said: '{user_input}'. "
    prompt += f"\n\nUser's financial profile:\n"
    prompt += f"Income: {profile.income}, Savings: {profile.savings}, Debts: {profile.debts}\n"
    prompt += f"Investments: {profile.investments}\n"
    prompt += f"Financial goals: {', '.join(profile.financial_goals)}\n"
    prompt += "\nProvide an empathetic response and appropriate financial advice, "
    prompt += "considering their emotional state, financial context, and profile information."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful AI financial advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# Backend: main.py
from fastapi import FastAPI
from app.routers import auth, profiles, chat
from app.database import database
from app.config import settings

app = FastAPI(
    title="AI Financial Advisor API",
    description="API for AI-powered financial advice for elderly and visually impaired users",
    version="0.2.0",
)

@app.on_event("startup")
async def startup_db_client():
    await database.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await database.close_database_connection()

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(chat.router)
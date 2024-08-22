# Backend: app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.DB_NAME]

    async def close_database_connection(self):
        if self.client:
            self.client.close()

database = Database()
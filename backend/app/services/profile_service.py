from app.models import UserProfile, SpendingEntry
from app.models import UserProfile
from app.database import database
from bson import ObjectId
from uuid import uuid4
import random
from datetime import datetime, timedelta


class ProfileService:
    @staticmethod
    async def create_profile(profile: UserProfile):
        profile_dict = profile.dict(exclude={"id"})
        profile_dict['_id'] = str(uuid4())
        result = await database.db.profiles.insert_one(profile_dict)
        profile.id = profile_dict['_id']
        return profile

    @staticmethod
    async def get_profile(profile_id: str):
        profile = await database.db.profiles.find_one({"_id": profile_id})
        if profile:
            profile['id'] = profile['_id']
            return UserProfile(**profile)
        return None

    @staticmethod
    async def update_profile(profile: UserProfile):
        await database.db.profiles.update_one(
            {"_id": profile.id},
            {"$set": profile.dict(exclude={"id"})}
        )
        return profile

    @staticmethod
    async def get_all_profiles():
        cursor = database.db.profiles.find({})
        profiles = await cursor.to_list(length=None)
        for profile in profiles:
            profile['id'] = str(profile['_id'])
        return [UserProfile(**profile) for profile in profiles]

    @staticmethod
    async def save_conversation(profile_id: str, user_message: str, ai_response: str, timestamp: str):
        await database.db.profiles.update_one(
            {"_id": profile_id},
            {"$push": {"conversation_history": {
                "user": user_message,
                "bot": ai_response,
                "timestamp": timestamp
            }}}
        )

    @staticmethod
    async def generate_synthetic_spending_data(profile_id: str, num_entries: int = 30):
        categories = ["Groceries", "Utilities", "Entertainment", "Transportation", "Dining Out", "Healthcare"]
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=num_entries)

        synthetic_data = []
        for i in range(num_entries):
            entry_date = (start_date + timedelta(days=i)).isoformat()  # Convert date to ISO format string
            category = random.choice(categories)
            amount = round(random.uniform(10, 200), 2)
            synthetic_data.append({
                "date": entry_date,
                "category": category,
                "amount": amount,
                "description": f"Synthetic {category} expense"
            })

        await database.db.profiles.update_one(
            {"_id": profile_id},
            {"$set": {"spending_data": synthetic_data}}
        )
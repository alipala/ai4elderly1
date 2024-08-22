from app.models import UserProfile
from app.database import database
from bson import ObjectId
from uuid import uuid4

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
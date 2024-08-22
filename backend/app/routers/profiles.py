from fastapi import APIRouter, Depends, HTTPException
from typing import List  # Add this import
from app.models import UserProfile
from app.services.profile_service import ProfileService
from app.dependencies import get_current_active_user

router = APIRouter()

@router.post("/create_profile", response_model=UserProfile)
async def create_profile(profile: UserProfile, current_user: dict = Depends(get_current_active_user)):
    return await ProfileService.create_profile(profile)

@router.get("/get_profile/{profile_id}", response_model=UserProfile)
async def get_profile(profile_id: str, current_user: dict = Depends(get_current_active_user)):
    profile = await ProfileService.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/update_profile/{profile_id}", response_model=UserProfile)
async def update_profile(profile_id: str, profile: UserProfile, current_user: dict = Depends(get_current_active_user)):
    existing_profile = await ProfileService.get_profile(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.id = profile_id
    updated_profile = await ProfileService.update_profile(profile)
    return updated_profile

@router.get("/get_all_profiles", response_model=List[UserProfile])
async def get_all_profiles(current_user: dict = Depends(get_current_active_user)):
    profiles = await ProfileService.get_all_profiles()
    return profiles
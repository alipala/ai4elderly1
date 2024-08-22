import os
from pydantic_settings import BaseSettings
from pydantic import ValidationError
import sys

class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str
    API_URL: str

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        env_file_encoding = 'utf-8'

try:
    settings = Settings()
except ValidationError as e:
    print(f"Error loading environment variables: {e}")
    print(f"Attempted to load .env from: {Settings.Config.env_file}")
    sys.exit(1)

# Print loaded settings for debugging
print("Loaded settings:")
for field, value in settings.dict().items():
    print(f"{field}: {'*' * len(value) if 'KEY' in field else value}")
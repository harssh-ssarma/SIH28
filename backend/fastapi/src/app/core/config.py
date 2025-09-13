from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    app_name: str = "SIH28 AI Service"
    debug: bool = config('DEBUG', default=False, cast=bool)
    api_key: str = config('API_KEY', default='your-api-key-here')
    
    class Config:
        env_file = ".env"

settings = Settings()
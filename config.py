from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    MODEL_NAME: str = "gpt-4"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

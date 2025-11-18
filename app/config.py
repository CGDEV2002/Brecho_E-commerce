from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Brechó E-commerce"
    DEBUG: bool = True
    SECRET_KEY: str = "admin@123"
    DATABASE_URL: str = "sqlite:///./brecho.db"

    class Config:
        env_file = ".env"

settings = Settings()
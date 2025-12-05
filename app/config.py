from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Brechó E-commerce"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "sua_chave_secreta_muito_segura_aqui_2024"
    DATABASE_URL: str = "sqlite:///./brecho.db"

    # JWT Settings
    JWT_SECRET_KEY: str = "jwt_secret_key_super_segura_2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_TIME: int = 30  # dias

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()


settings = get_settings()

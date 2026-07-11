from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jarvis Crypto AI"
    TELEGRAM_BOT_TOKEN: str = "test_token"
    OPENAI_API_KEY: str = "test_key"
    ENVIRONMENT: str = "production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #App settings read from environment variables or a local .env file. 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"


settings = Settings()

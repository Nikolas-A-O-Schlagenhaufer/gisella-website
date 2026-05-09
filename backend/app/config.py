from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = (  # pyright: ignore[reportUnannotatedClassAttribute]
        SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    )

    secret_key: SecretStr
    algorith: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()  # pyright: ignore[reportCallIssue]

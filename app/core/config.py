from pydantic_settings import BaseSettings        # ← изменили
from pydantic import Field                        # Field остаётся в pydantic

class Settings(BaseSettings):
    project_name: str = "auth-service"

    database_url: str = Field(..., env="DATABASE_URL")

    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_exp: int = 60 * 60          # 1 час

    environment: str = Field(default="local", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

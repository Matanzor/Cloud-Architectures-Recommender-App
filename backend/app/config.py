from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    db_name: str = "cloud_architectures"

    class Config:
        env_file = ".env"


settings = Settings()

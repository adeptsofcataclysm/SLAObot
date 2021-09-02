from pydantic import BaseSettings


class Settings(BaseSettings):

    class Config:
        env_file = '.env'

    wcl_client_id: str
    wcl_client_secret: str

    discord_token: str


settings = Settings()

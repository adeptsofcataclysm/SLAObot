from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    class Config:
        env_file = '.env'

    wcl_client_id: str
    wcl_client_secret: str

    discord_token: str

    command_prefix: str = 'slao'

    signup_channel_id: int


settings = Settings()

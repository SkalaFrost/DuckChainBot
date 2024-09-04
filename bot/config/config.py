from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 1
    API_HASH: str = ""
   
    REF_ID: str = ''
    TAP: bool = False
    SLEEP_TIME: list = [300,600]
    AUTO_TASK: bool = True
    USE_PROXY_FROM_FILE: bool = False


settings = Settings()



from pydantic import BaseSettings, Field


# from dotenv import load_dotenv


# load_dotenv()

class LoggingConfig(BaseSettings):
    level: str = "INFO"
    filepath: str = "archivist.log"


class Config(BaseSettings):
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_database: str = Field(..., env="NOTION_DATABASE")
    telegram_token: str = Field(..., env="TELEGRAM_TOKEN")
    telegram_user: str = Field(..., env="TELEGRAM_USER")
    logging: LoggingConfig = LoggingConfig()

    class Config:
        arbitrary_types_allowed = True

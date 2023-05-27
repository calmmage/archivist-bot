from pydantic import BaseSettings, Field


from dotenv import load_dotenv
load_dotenv()

class LoggingConfig(BaseSettings):
    level: str = Field(default="INFO", env="LOGGING_LEVEL")
    filepath: str = Field(None, env="LOGGING_FILEPATH")


class AppConfig(BaseSettings):
    # todo: auto-create commands to edit these
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_db_id: str = Field(..., env="NOTION_DB_ID")


class BotConfig(BaseSettings):
    telegram_token: str = Field(..., env="TELEGRAM_TOKEN")
    telegram_user_id: str = Field(..., env="TELEGRAM_USER_ID")

    # todo: auto-create commands to edit these
    delete_timeout: int = Field(60, env="ARCHIVIST_DELETE_TIMEOUT")
    peek_count: int = Field(5, env="ARCHIVIST_PEEK_COUNT")
    peek_timeout: int = Field(60, env="ARCHIVIST_PEEK_TIMEOUT")

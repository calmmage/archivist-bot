import argparse
from loguru import logger

from archivist_bot.app import App
from archivist_bot.bot import Bot


def main():
    parser = argparse.ArgumentParser(description="Archivist Telegram Bot")
    parser.add_argument("--telegram-token", help="Your Telegram Bot token")
    parser.add_argument("--telegram-user-id", help="Your Telegram user ID")
    parser.add_argument("--notion-token", help="Your Notion token")
    parser.add_argument("--notion-db-id", help="Your Notion database ID")
    # # todo: add these
    # delete_timeout: int = Field(60, "ARCHIVIST_DELETE_TIMEOUT")
    # peek_count: int = Field(5, "ARCHIVIST_PEEK_COUNT")
    # peek_timeout: int = Field(60, "ARCHIVIST_PEEK_TIMEOUT")

    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()

    import sys
    from archivist_bot.config import LoggingConfig

    logging_config = LoggingConfig(level="DEBUG" if args.debug else "INFO")
    # set logging level
    logger.remove()
    # set up console logger
    logger.add(sys.stdout,
               level=logging_config.level,
               # rotation="1 week",
               serialize=False)
    # file logger
    if logging_config.filepath:
        logger.add(logging_config.filepath,
                   level=logging_config.level,
                   # rotation="1 week",
                   serialize=False)
    logger.info("Logging configured")
    app = App(
        # notion_token=args.notion_token,
        # notion_db_id=args.notion_db_id,
    )
    bot = Bot(
        app,
        # telegram_token=args.telegram_token,
        # telegram_user_id=args.telegram_user_id
    )
    bot.run()


if __name__ == "__main__":
    main()

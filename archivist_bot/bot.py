import asyncio
import textwrap
from loguru import logger
from telegram import __version__ as TG_VER

from archivist_bot.app import App, AppResponseStatus
from archivist_bot.config import BotConfig

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, \
    MessageHandler, filters


class Bot:
    def __init__(self, app: App, **kwargs) -> None:
        logger.info("Initializing Bot")
        self.app = app
        self.config = BotConfig(**kwargs)
        token = self.config.telegram_token
        self.application = Application.builder().token(token).post_init(
            self.post_init).build()

        self.application.add_handler(
            CommandHandler("start", self.start_command))
        self.application.add_handler(
            CommandHandler("peek", self.peek_command,
                           filters.User(
                               username=f"@{self.config.telegram_user_id}"))
        )

        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND &
                           filters.User(
                               username=f"@{self.config.telegram_user_id}"
                           ),
                           self.message_handler))
        logger.info("Bot initialized")

    @staticmethod
    async def post_init(application: Application):
        await application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("peek", "Peek at the last saved messages")
        ])

    def run(self):
        logger.info("Starting Bot")
        self.application.run_polling()

    async def start_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Received /start command")
        user = update.effective_user
        if user.username != self.config.telegram_user_id:
            logger.info(f"User {user.username} is not authorized")
            await update.message.reply_text(
                "You are not authorized to use this bot. "
                "Please contact the bot owner for more details."
            )
            return

        db_url = self.app.db_url
        welcome_message = textwrap.dedent(f"""
            Hi *{user.full_name}*! I'm the Archivist Bot.
            I will save your messages to a Notion database.
            The link to the Notion database is [here]({db_url})
        """)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_message,
            parse_mode='Markdown'
        )

        # Pin the message
        await context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=message.message_id
        )
        logger.info("Sent welcome message and pinned it")

    async def message_handler(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Processing message")
        message_text = update.message.text
        result = await self.app.process_message_async(message_text)

        if result.status == AppResponseStatus.SUCCESS:
            logger.info("Message saved successfully")
            temp_message = await update.message.reply_text("🍾 Message saved!")
            await asyncio.sleep(self.config.delete_timeout)
            await update.message.delete()
            await temp_message.delete()
        else:
            # Notify user of failure
            await update.message.reply_text("❌ Failed to save message!")
            logger.error(f"Failed to save message: {message_text}")

    async def peek_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Received /peek command")
        messages = await self.app.get_messages_async(
            limit=self.config.peek_count)
        logger.debug(f"Extracted {len(messages)} messages")
        peek_messages = []
        for message in messages:
            logger.debug(f"Sending peek message: {message}")
            peek_message = await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            peek_messages.append(peek_message)
            await asyncio.sleep(1)
        logger.debug(f"Sent {len(peek_messages)} peek messages")
        await asyncio.sleep(self.config.peek_timeout)

        for peek_message in peek_messages:
            await peek_message.delete()
            await asyncio.sleep(1)
        await update.message.delete()
        logger.info("Finished /peek command execution")


if __name__ == '__main__':
    import sys
    from config import LoggingConfig

    logging_config = LoggingConfig()
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

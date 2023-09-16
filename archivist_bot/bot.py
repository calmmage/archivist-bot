import asyncio
import textwrap
from typing import Union, List

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
from telegram import Update, Message, File
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

        self.commands = [
            ("start", "Start the bot"),
            ("peek", "Peek at the last saved messages")
        ]

        self.application.add_handler(
            CommandHandler("start", self.start_command))
        self.application.add_handler(
            CommandHandler("peek", self.peek_command, self.user_filter)
        )

        self.application.add_handler(
            MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO |
                            filters.VOICE | filters.AUDIO) & ~filters.COMMAND &
                           self.user_filter,
                           self.message_handler)
        )
        logger.info("Bot initialized")

    async def post_init(self, application: Application):
        await application.bot.set_my_commands(self.commands)

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

    @staticmethod
    def extract_message_text(update: Update):
        """Gracefully extract text or captions from the text"""
        return update.message.text or update.message.caption

    @staticmethod
    async def extract_message_content(update: Update) -> File:
        """Gracefully extract text or captions from the text"""
        message = update.message
        # todo: test and handle each type correctly
        # todo: support multiple items? How are they delivered? test.
        if message.photo:
            return await message.photo[1].get_file()
        if message.video:
            return await message.video.get_file()
        if message.audio:
            return await message.audio.get_file()
        if message.voice:
            return await message.voice.get_file()
        return None

    async def message_handler(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Processing message")
        message_text = self.extract_message_text(update)
        content = await self.extract_message_content(update)
        content_links = [content._get_encoded_url() if content else None]
        result = await self.app.process_message_async(message_text,
                                                      content_links)  # todo:
        # content

        if result.status == AppResponseStatus.SUCCESS:
            logger.info("Message saved successfully")
            temp_message = await update.message.reply_text("🍾 Message saved!")
            await self.cleanup([update.message, temp_message])
        else:
            # Notify user of failure
            await update.message.reply_text("❌ Failed to save message!")
            logger.error(f"Failed to save message: {message_text}")

    @property
    def user_filter(self):
        return filters.User(username=f"@{self.config.telegram_user_id}")

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
        await self.cleanup(peek_messages, self.config.peek_timeout)
        await update.message.delete()
        logger.info("Finished /peek command execution")

    async def cleanup(self, msgs: Union[Message, List[Message]], timeout=None):
        if timeout is None:
            timeout = self.config.delete_timeout
        await asyncio.sleep(timeout)
        if not isinstance(msgs, list):
            msgs = [msgs]
        for msg in msgs:
            await msg.delete()

    def setup_config_commands(self):
        for attribute in ["peek_timeout", "peek_count", "delete_timeout"]:
            for action in ["set", "get"]:
                key = f"{action}_{attribute}"
                self.commands.append(
                    (key, f"{action} the {attribute} config attribute")
                )
                command = self.config_int_attribute_command(attribute, action)
                self.application.add_handler(
                    CommandHandler(key, command, self.user_filter)
                )

    def config_int_attribute_command(self, attribute, action):
        async def command(update: Update, context) -> None:
            logger.info(f"Received /{action}_{attribute} command")
            if action == "set":
                try:
                    val = int(context.args[0])
                    setattr(self.config, attribute, val)
                    msg = await update.message.reply_text(
                        f"{attribute} is set to {val}"
                    )
                    logger.info(f"{attribute} is set to {val}")
                    await self.cleanup(msg)
                except (IndexError, ValueError):
                    # todo: make a conversation to request a new value
                    msg = await update.message.reply_text(
                        "Please specify a valid int attribute value"
                    )
                    await self.cleanup(msg)
                    return

        return command


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

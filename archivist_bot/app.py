from loguru import logger
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    # Filters,
    CallbackContext,
)
from archivist_bot.config import Config


class App:
    def __init__(self, **kwargs) -> None:
        self.config = Config(**kwargs)

        self.updater = Updater(token=self.config.telegram_token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command,
                           self.archive_message)
        )

    def start(self, update: Update, context: CallbackContext) -> None:
        """Send a welcome message and the Notion link to the user."""
        user_id = update.effective_user.id
        welcome_message = "Welcome to Archivist Bot!\n\nThis bot helps you archive messages.\n\nTo get started, send any message and it will be saved."

        # Add Notion link customization here
        notion_link = "https://www.notion.so/"

        reply_markup = ReplyKeyboardMarkup(
            [["Notion Link"]],
            resize_keyboard=True,
        )

        context.bot.send_message(
            chat_id=user_id,
            text=f"{welcome_message}\n\nClick [here]({notion_link}) to access the Notion link.",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup,
        )

    def archive_message(self, update: Update, context: CallbackContext) -> None:
        """Archive the received message to the desired storage."""
        message = update.effective_message
        user_id = update.effective_user.id

        # Save the message to your desired storage (Notion, database, etc.)
        # Replace this with your implementation logic
        # notion.save_message(message.text)

        # Delete the message after archiving
        message.delete()

    def run(self) -> None:
        """Run the bot."""
        self.updater.start_polling()
        self.updater.idle()


def main(debug: bool = False) -> None:
    import argparse
    # Configure loguru based on debug flag
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add()
    logger.add("archivist.log", rotation="1 day",
               level=level)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Archivist Telegram Bot")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    args = parser.parse_args()

    kwargs = {}
    if args.debug:
        kwargs["logging"] = {"level": "DEBUG"}

    app = App(**kwargs)
    app.run()


if __name__ == "__main__":
    main()

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from .notion_handler import NotionHandler

class BotHandler:
    def __init__(self, token: str, user_id: str, notion: NotionHandler):
        self.updater = Updater(token=token, use_context=True)
        self.user_id = user_id
        self.notion = notion

        self.updater.dispatcher.add_handler(CommandHandler("start", self.start))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.save_message))

    def start(self, update, context):
        """
        Send a message when the command /start is issued.
        """
        # Send a message with the link to the Notion database
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="The link to the Notion database is [here](<Your Notion database link>)",
            parse_mode='Markdown'
        )

        # Pin the message
        context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=message.message_id
        )

    def save_message(self, update, context):
        if update.effective_chat.id != self.user_id:
            return
        message_text = update.message.text
        self.notion.save_message(message_text)
        update.message.delete()

    def start(self):
        self.updater.start_polling()

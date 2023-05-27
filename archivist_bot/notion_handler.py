from loguru import logger
from notion_client import Client


class NotionHandler:
    def __init__(self, token: str, db_id: str):
        logger.debug("Initializing NotionHandler")
        self.client = Client(auth=token)
        self.db_id = db_id
        logger.debug("NotionHandler initialized")

    def get_url(self):
        logger.debug("Generating database URL")
        return "https://www.notion.so/{}".format(self.db_id)

    @staticmethod
    def generate_page_title(message_text: str):
        logger.debug("Generating page title from message text")
        return message_text.split("\n")[0]

    def get_messages(self):
        logger.debug("Retrieving messages from Notion database")
        return self.client.databases.query(database_id=self.db_id)

    async def get_messages_async(self, limit=None):
        logger.debug("Retrieving messages from Notion database asynchronously")
        messages = await self.client.databases.query(database_id=self.db_id,
                                                     limit=limit)
        return [self._get_message_text(message) for message in messages[
            "results"]]

    def compose_request(self, message_text: str):
        logger.debug("Composing request for Notion database")
        return {
            "parent": {
                "database_id": self.db_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": self.generate_page_title(
                                    message_text),
                            }
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": message_text
                                }
                            }
                        ]
                    }
                }
            ]
        }

    @staticmethod
    def _get_message_text(message):
        # Assuming that the first block is the one with the message text
        return message["children"][0]["paragraph"]["text"][0]['text']['content']

    def save_message(self, message_text: str):
        logger.debug("Saving message to Notion database")
        new_page = self.compose_request(message_text)
        self.client.pages.create(**new_page)
        logger.debug("Message saved to Notion database")

    async def save_message_async(self, message_text: str):
        logger.debug("Saving message to Notion database asynchronously")
        new_page = self.compose_request(message_text)
        await self.client.pages.create(**new_page)
        logger.debug("Message saved to Notion database asynchronously")

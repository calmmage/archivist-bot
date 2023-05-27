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
        # messages = await self.client.databases.query(database_id=self.db_id,
        #                                              limit=limit)
        pages = self.client.databases.query(database_id=self.db_id,
                                            limit=limit)
        return [self._get_message_text(page) for page in pages[
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
                        "rich_text": [
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

    def _get_message_text(self, page):
        page_id = page["id"]
        # retrieve page content
        response = self.client.blocks.children.list(block_id=page_id)
        children = []
        for child in response["results"]:
            child_text = child["paragraph"]["rich_text"][0]['text']['content']
            children.append(child_text)
        title = page['properties']['Name']['title'][0]['text']['content']

        return f"*{title}*\n" + "\n".join(children)

    async def save_message(self, message_text: str):
        logger.debug("Saving message to Notion database asynchronously")
        new_page = self.compose_request(message_text)
        self.client.pages.create(**new_page)
        # await self.client.pages.create(**new_page)
        logger.debug("Message saved to Notion database asynchronously")

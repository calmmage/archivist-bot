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

    def compose_request(self, message_text: str, content_links):
        logger.debug("Composing request for Notion database")
        # todo: add content links
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
        children = self._load_blocks(page["id"])
        return self._construct_text(page, children)

    def _load_blocks(self, block_id, depth=0, max_depth=10):
        if depth > max_depth:
            return []

        response = self.client.blocks.children.list(block_id=block_id)
        children = []
        for child in response["results"]:
            child_item = child.get("paragraph", {}).get("rich_text")
            if child_item:
                child_text = child_item[0]['text']['content']
            else:
                child_text = ""
            child_blocks = self._load_blocks(child["id"], depth=depth + 1,
                                             max_depth=max_depth)
            children.append((child_text, child_blocks))

        return children

    def _construct_text(self, page, children, depth=0, sep="  "):
        if isinstance(page, str):
            # This is a leaf node
            text = sep * depth + page
        elif "properties" in page:
            title = page['properties']['Name']['title'][0]['text'][
                'content']
            text = sep * depth + f"*{title}*\n" if title else ""
        else:
            text = ""

        for child, subchildren in children:
            text += self._construct_text(child, subchildren, depth=depth + 1,
                                         sep=sep)

        return text

    async def save_message(self, message_text: str, content_links: list = None):
        logger.debug("Saving message to Notion database asynchronously")
        new_page = self.compose_request(message_text, content_links)
        self.client.pages.create(**new_page)
        # await self.client.pages.create(**new_page)
        logger.debug("Message saved to Notion database asynchronously")

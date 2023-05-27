from notion_client import Client
import os

class NotionHandler:
    def __init__(self, token: str, db_id: str):
        self.client = Client(auth=token)
        self.db_id = db_id

    def save_message(self, message_text: str):
        new_page = {
            "Body": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": message_text},
                    },
                ],
            },
        }
        self.client.pages.create(parent={"database_id": self.db_id}, properties=new_page)

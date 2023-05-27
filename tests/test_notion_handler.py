import unittest
from unittest.mock import patch, MagicMock

from archivist_bot.notion_handler import NotionHandler


class TestNotionHandler(unittest.TestCase):
    @patch('notion_client.Client')
    def test_init(self, mock_client):
        handler = NotionHandler("test_token", "test_db_id")

        mock_client.assert_called_once_with(auth="test_token")
        self.assertEqual(handler.db_id, "test_db_id")

    def test_get_url(self):
        handler = NotionHandler("test_token", "test_db_id")

        expected_url = "https://www.notion.so/test_db_id"
        self.assertEqual(handler.get_url(), expected_url)

    def test_generate_page_title(self):
        handler = NotionHandler("test_token", "test_db_id")
        message_text = "Title\nBody"

        self.assertEqual(handler.generate_page_title(message_text), "Title")

    @patch('notion_client.Client')
    def test_save_message(self, mock_client):
        handler = NotionHandler("test_token", "test_db_id")
        mock_create = MagicMock()
        mock_client.pages.create = mock_create

        handler.save_message_async("test_message")
        mock_create.assert_called_once()

    @patch('notion_client.Client')
    def test_get_messages(self, mock_client):
        handler = NotionHandler("test_token", "test_db_id")
        mock_query = MagicMock()
        mock_client.databases.query = mock_query

        handler.get_messages()
        mock_query.assert_called_once()


if __name__ == "__main__":
    unittest.main()

# import pytest
# from unittest import mock
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import CallbackContext
# from archivist_bot.app import App
#
#
# @pytest.fixture
# def app():
#     app = App()
#     return app
#
#
# def test_start(app, mocker):
#     update = mock.Mock(spec=Update)
#     context = mock.Mock(spec=CallbackContext)
#
#     app.start(update, context)
#
#     context.bot.send_message.assert_called_once_with(
#         chat_id=update.effective_user.id,
#         text=mock.ANY,
#         parse_mode="MarkdownV2",
#         reply_markup=mock.ANY,
#     )
#
#
# def test_archive_message(app, mocker):
#     update = mock.Mock(spec=Update)
#     message = mock.Mock()
#     user_id = 123
#
#     update.effective_message = message
#     update.effective_user.id = user_id
#
#     app.archive_message(update, None)
#
#     message.delete.assert_called_once()
#
#
# def test_run(app, mocker):
#     updater = mock.Mock()
#     dispatcher = mock.Mock()
#     app.updater = updater
#     app.dispatcher = dispatcher
#
#     app.run()
#
#     updater.start_polling.assert_called_once()
#     updater.idle.assert_called_once()

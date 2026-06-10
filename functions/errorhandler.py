import html
import json
import logging
import traceback
import os
from os.path import join, dirname
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler



def error_handler(update: object, context: CallbackContext) -> None:
    """Handles errors occurred during bot execution.

    Logs the error and sends a formatted stack trace to the developer.

    Args:
        update (object): The update object that caused the error.
        context (CallbackContext): The context of the error.
    """
    DEVELOPER_CHAT_ID = os.environ.get("DEVELOPER_CHAT_ID")

    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    if DEVELOPER_CHAT_ID:
        context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

# Helper functions for error messages and string builder

def bonk(update : Update , texts , lang):
    """Notifies the user of an invalid input.

    Sends an error message and a specific photo ("bonk") to the user.

    Args:
        update (Update): The Telegram update object.
        texts (dict): Dictionary of localized texts.
        lang (str): The language code (e.g., 'en', 'it').
    """
    update.message.reply_text(texts[lang]["texts"]['error']) 
    update.message.reply_photo(photo = open(join(dirname(__name__), 'photos/bonk.jpg'),'rb'))    


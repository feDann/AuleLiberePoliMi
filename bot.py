import os
from os.path import join , dirname
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater , CommandHandler
from utils.free_classroom import find_free_room
import json
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


TOKEN = os.environ.get("TOKEN")

location = {}
with open(join(dirname(__file__), 'location.json')) as location_json:
    location = json.load(location_json)
    print(location)


START_KEYBOARD = [['🔍Rooms' ,'⚙Settings']]




def start(update, context):
    reply_markup = ReplyKeyboardMarkup(START_KEYBOARD)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Find free rooms" , reply_markup= reply_markup)



def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher
    start_handlr = CommandHandler('start' ,start)

    commands = [start_handlr]
    for command in commands:
        dispatcher.add_handler(command)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


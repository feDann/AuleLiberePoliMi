import os
from os.path import join , dirname
from dotenv import load_dotenv
from telegram.message import Message
from telegram.utils.helpers import UTC
from utils import free_classroom
from utils.free_classroom import find_free_room
import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import (Updater,CommandHandler,CallbackQueryHandler,ConversationHandler,CallbackContext,MessageHandler , Filters, messagehandler)
from datetime import datetime ,date , timedelta
from telegram import ParseMode


# Config Stuff
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

location = {}
with open(join(dirname(__file__), 'json/location.json')) as location_json:
    location = json.load(location_json)

texts = {}
with open(join(dirname(__file__), 'json/lang/en.json')) as text_json:
    texts = json.load(text_json)



TOKEN = os.environ.get("TOKEN")

# States for conversation handler
LOCATION , DAY , START_TIME , END_TIME, END = range(5)
date_regex = '^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'
initial_keyboards = [["🔍Search" , "ℹinfo"]]


# Helper functions for error messages and string builder

def bonk(update):
    update.message.reply_text(texts['error']) 
    update.message.reply_photo(photo = open(join(dirname(__file__), 'photos/bonk.jpg'),'rb'))    

def room_builder_str(available_rooms):
    available_rooms_str = ""
    for building in available_rooms:
        available_rooms_str += '\n<b>' + building + '</b>\n'
        for room in available_rooms[building]:
            available_rooms_str += '\t' + room + '\n'
    return available_rooms_str


# Functions to handle all the states

def start(update: Update , context: CallbackContext) ->int:

    user = update.message.from_user
    logger.info("%s started conversation" , user.username)

    update.message.reply_text(texts['welcome'].format(user.username),disable_web_page_preview=True , parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboards))

    return LOCATION

def choose_location_state(update: Update , context: CallbackContext) ->int:
    reply_keyboard = [[x]for x in location]
    
    user = update.message.from_user
    logger.info("%s in  choose location state" , user.username)
    
    update.message.reply_text(texts['location'] , reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True))

    return DAY

def choose_day_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    location_text = update.message.text
    logger.info("%s in  choose location state" , user.username)

    if location_text not in location:
        bonk(update)
        return DAY
    
    context.user_data["location"] = location_text

    reply_keyboard = [[(date.today() + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
    update.message.reply_text(texts['day'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return START_TIME

def choose_start_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    date_text = update.message.text
    logger.info("%s in  choose start time state" , user.username)
    
    if date_text != 'Today' and date_text != 'Tomorrow':
        date_date = datetime.strptime(date_text, '%d/%m/%Y').date()
        print(date_date)
        if date_date < date.today() or date_date > (date.today() + timedelta(days=7)):
            bonk(update)
            return START_TIME
    else:
        date_text = date.today().strftime("%d/%m/%Y") if date_text == 'Today' else (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    context.user_data['date'] = date_text

    reply_keyboard = [[x] for x in range(8,20)]
    update.message.reply_text(texts['starting_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    
    return END_TIME

def choose_end_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    start_text = update.message.text
    logger.info("%s in  choose end time state" , user.username)
    try:
        start_time = int(start_text)
        if start_time > 20 or start_time < 8:
            bonk(update)
            return END_TIME
    except:
        bonk(update)
        return END_TIME

    context.user_data['start_time'] = start_text
    reply_keyboard = [[x] for x in range(int(start_text) + 1 , 21)]
    update.message.reply_text(texts['ending_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return END

def end_state(update: Update , context: CallbackContext) ->int:
    global location
    user = update.message.from_user
    end_time = update.message.text
    logger.info("%s in the end state" , user.username)    

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    _location = context.user_data['location']
    
    try:
        if int(start_time) >= int(end_time) or int(end_time) > 21:
            bonk(update)
            return END
    except:
        bonk(update)
        return END
    
    day , month , year = date.split('/')
    available_rooms = find_free_room(int(start_time) , int(end_time) , location[_location],int(day) , int(month) , int(year))  
    update.message.reply_text(room_builder_str(available_rooms),parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboards))

    return LOCATION


def terminate(update: Update, _: CallbackContext) -> int:
    # terminate the conversation
    user = update.message.from_user
    logger.info("User %s terminated the conversation.", user.username)
    update.message.reply_text(texts['cancel'], reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def info(update: Update, _: CallbackContext):
    user = update.message.from_user
    logger.info("User %s asked for more info.", user.username)
    update.message.reply_text(texts['info'],parse_mode=ParseMode.HTML)
    return 

# Create the bot and all the necessary handler

def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            LOCATION : [MessageHandler(Filters.regex('^(🔍Search)$'),choose_location_state)],
            DAY : [MessageHandler(Filters.text & ~Filters.command,choose_day_state)],
            START_TIME : [MessageHandler(Filters.regex(date_regex) | Filters.regex('^(Today)$') | Filters.regex('^(Tomorrow)$'), choose_start_time_state )],
            END_TIME : [MessageHandler(Filters.text ,choose_end_time_state)],
            END : [MessageHandler(Filters.text , end_state)]
            },
        fallbacks=[CommandHandler('terminate' , terminate) , MessageHandler(Filters.regex('^(ℹinfo)$') , info)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


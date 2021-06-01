import os
from os.path import join , dirname
from dotenv import load_dotenv
from telegram.message import Message
from utils.free_classroom import find_free_room
import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import (Updater,CommandHandler,CallbackQueryHandler,ConversationHandler,CallbackContext,MessageHandler , Filters, messagehandler)
from datetime import datetime ,date , timedelta

# Config Stuff
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

location = {}
with open(join(dirname(__file__), 'location.json')) as location_json:
    location = json.load(location_json)

TOKEN = os.environ.get("TOKEN")

# States for conversation handler
LOCATION , DAY , START_TIME , END_TIME, END = range(5)
date_regex = '^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'

def start(update: Update , context: CallbackContext) ->int:
    reply_keyboard = [['🔍Search' , 'ℹinfo']]

    user = update.message.from_user
    logger.info("%s started conversation" , user.username)

    update.message.reply_text('Test' , reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return LOCATION

def choose_location_state(update: Update , context: CallbackContext) ->int:
    reply_keyboard = [[x]for x in location]
    
    user = update.message.from_user
    logger.info("%s in  choose location state" , user.username)
    
    update.message.reply_text('Choose a Location' , reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True))

    return DAY

def choose_day_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    location_text = update.message.text
    logger.info("%s in  choose location state" , user.username)

    if location_text not in location:
        update.message.reply_text('Insert a valid location or use /cancel to stop the search')
        return DAY
    
    context.user_data["location_state"] = location_text
    print(context.user_data)

    reply_keyboard = [[(date.today() + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
    update.message.reply_text('Choose a day',reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return START_TIME

def choose_start_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    date_text = update.message.text
    logger.info("%s in  choose day state" , user.username)
    
    if date_text != 'Today' and date_text != 'Tomorrow':
        date_date = datetime.strptime(date_text, '%d/%m/%Y')
        if date_date < date.today().strftime("%d/%m/%Y") or date_date > (date.today() + timedelta(days=7)).strftime("%d/%m/%Y"):
            reply_keyboard = [[(date.today() + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
            update.message.reply_text('Please use a button to choose the day or press /cancel',reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )
            return START_TIME
    else:
        date_text = date.today().strftime("%d/%m/%Y") if date_text == 'Today' else (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    context.user_data['date'] = date_text

    reply_keyboard = [[x] for x in range(8,21)]
    update.message.reply_text('Choose the starging time',reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    
    return END_TIME

def choose_end_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    start_text = update.message.text
    logger.info("%s in  choose day state" , user.username)



def cancel(update: Update, _: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.username)

    reply_keyboard = [['🔍Search' , 'ℹinfo']]

    update.message.reply_text('Search canceled!\nPress the search button to start a new search or info to get additional infos!', reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return ConversationHandler.END

def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            LOCATION : [MessageHandler(Filters.regex('^(🔍Search)$'),choose_location_state)],
            DAY : [MessageHandler(Filters.text,choose_day_state)],
            START_TIME : [MessageHandler(Filters.regex(date_regex) | Filters.regex('^(Today)$') | Filters.regex('^(Tomorrow)$'), choose_start_time_state )],
            END_TIME : [MessageHandler(Filters.regex('/[14-21]/'),choose_end_time_state)]
            },
        fallbacks=[CommandHandler('cancel' , cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


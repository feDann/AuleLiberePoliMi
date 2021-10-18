import os
import time
import sys
import pytz
import json
import logging
from os.path import join , dirname
from dotenv import load_dotenv
import telegram
from utils.free_classroom import find_free_room
from utils.find_classrooms import TIME_SHIFT , MAX_TIME , MIN_TIME
from telegram import  Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import (PicklePersistence,Updater,CommandHandler,ConversationHandler,CallbackContext,MessageHandler , Filters)
from datetime import datetime , timedelta
from telegram import ParseMode
from functions import errorhandler , string_builder , input_check


LOGPATH = "log/"
DIRPATH = dirname(__file__)


# Config Stuff

if not os.path.exists(LOGPATH):
    os.mkdir(LOGPATH)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("{0}{1}.log".format(LOGPATH, str(time.time()))),
        logging.StreamHandler(sys.stdout)
    ]
)

dotenv_path = join(DIRPATH, '.env')
load_dotenv(dotenv_path)





# Load query arguments for Location as a dict
location_dict = {}
with open(join(DIRPATH, 'json/location.json')) as location_json:
    location_dict = json.load(location_json)

# Load the text messages for all the different languages
texts = {}
for lang in os.listdir(join(DIRPATH , 'json/lang')):
    with open(join(DIRPATH,'json' , 'lang' , lang) , 'r') as f:
        texts[lang[:2]] = json.load(f)


TOKEN = os.environ.get("TOKEN")

texts = texts['en']





# States for conversation handler
LOCATION , DAY , START_TIME , END_TIME, END , SETLOCPREF = range(6)
date_regex = '^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})$'
initial_keyboards = [["🔍Search" , "ℹinfo" ],["🕒Now"]]






# Functions to handle all the states

def start(update: Update , context: CallbackContext) ->int:
    
    context.user_data.clear()

    user = update.message.from_user
    logging.info("%s started conversation" , user.username)

    update.message.reply_text(texts['welcome'].format(user.username),disable_web_page_preview=True , parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboards))

    return LOCATION

def find_now(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    logging.info("%s in find_now state" , user.username)

    if "location_preference" in context.user_data:
        start_time = int(datetime.now(pytz.timezone('Europe/Rome')).strftime('%H'))
        if start_time > MAX_TIME or start_time < MIN_TIME:
            update.message.reply_text(texts['ops'])
            start_time = MIN_TIME
        end_time = start_time + 2
        context.user_data["location"] = context.user_data["location_preference"]    
        context.user_data["date"] = datetime.now(pytz.timezone('Europe/Rome')).strftime("%d/%m/%Y")
        context.user_data["start_time"] = start_time
        update.message.text = end_time
        return end_state(update, context)
    else:
        reply_keyboard = [[x]for x in location_dict]
        update.message.reply_text(texts['location'] , reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True))
        return SETLOCPREF


def set_location_preference(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in set location preference" , user.username)

    if not input_check.location_check(message,location_dict):
        errorhandler.bonk(update , texts)
        return SETLOCPREF
    
    context.user_data["location_preference"] = message
    update.message.reply_text(texts['location_success'], reply_markup=ReplyKeyboardMarkup(initial_keyboards))

    return LOCATION



def choose_location_state(update: Update , context: CallbackContext) ->int:
    reply_keyboard = [[x]for x in location_dict]
    
    user = update.message.from_user
    logging.info("%s in  choose location state" , user.username)
    
    update.message.reply_text(texts['location'] , reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True))

    return DAY



def choose_day_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  choose location state" , user.username)

    if not input_check.location_check(message,location_dict):
        errorhandler.bonk(update , texts)
        return DAY
    
    context.user_data["location"] = message

    reply_keyboard = [[(datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
    update.message.reply_text(texts['day'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return START_TIME



def choose_start_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  choose start time state" , user.username)
    
    if input_check.day_check(message):
        current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
        message = current_date.strftime("%d/%m/%Y") if message == 'Today' else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        errorhandler.bonk(update, texts)
        return START_TIME

    context.user_data['date'] = message
    reply_keyboard = [[x] for x in range(MIN_TIME,MAX_TIME)]
    update.message.reply_text(texts['starting_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )
    
    return END_TIME



def choose_end_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  choose end time state" , user.username)
    ret,start_time = input_check.start_time_check(message)
    
    if not ret:
        errorhandler.bonk(update , texts)
        return END_TIME

    context.user_data['start_time'] = start_time
    reply_keyboard = [[x] for x in range(start_time + 1 , MAX_TIME + 1)]
    update.message.reply_text(texts['ending_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return END

def end_state(update: Update , context: CallbackContext) ->int:
    global location
    user = update.message.from_user
    message = update.message.text

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    location = context.user_data['location']
    ret ,end_time = input_check.end_time_check(message ,start_time)

    if not ret:
        errorhandler.bonk(update , texts)
        return END

    logging.info("%s in the end state" , user.username)
    
    day , month , year = date.split('/')
    available_rooms = find_free_room(float(start_time + TIME_SHIFT) , float(end_time + TIME_SHIFT) , location_dict[location],int(day) , int(month) , int(year))  
    for m in string_builder.room_builder_str(available_rooms):
        update.message.reply_chat_action(telegram.ChatAction.TYPING)
        update.message.reply_text(m,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboards))
    
    logging.info("%s search was: %s %s %d %d" , user.username , location , date , start_time , end_time )
    
    
    if "location_preference" in context.user_data:
        pref = context.user_data["location_preference"]
        context.user_data.clear()
        context.user_data["location_preference"] = pref
    else:
        context.user_data.clear()
    return LOCATION



# fallback funtions

def terminate(update: Update, _: CallbackContext) -> int:
    # terminate the conversation
    user = update.message.from_user
    logging.info("%s terminated the conversation.", user.username)
    update.message.reply_text(texts['cancel'], reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def info(update: Update, _: CallbackContext):
    user = update.message.from_user
    logging.info("User %s asked for more info.", user.username)
    update.message.reply_text(texts['info'],parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboards))
    return 


# Create the bot and all the necessary handler


def main():
    #add persistence for states
    pp = PicklePersistence(filename='aulelibere_pp')

    updater = Updater(token=TOKEN , use_context=True , persistence=pp)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            SETLOCPREF : [MessageHandler(Filters.text & ~Filters.command, set_location_preference)],
            LOCATION : [MessageHandler(Filters.regex('^(🔍Search)$'),choose_location_state)],
            DAY : [MessageHandler(Filters.text & ~Filters.command,choose_day_state)],
            START_TIME : [MessageHandler(Filters.regex(date_regex) | Filters.regex('^(Today)$') | Filters.regex('^(Tomorrow)$'), choose_start_time_state )],
            END_TIME : [MessageHandler(Filters.text & ~Filters.command,choose_end_time_state)],
            END : [MessageHandler(Filters.text & ~Filters.command, end_state)]
            },
        fallbacks=[MessageHandler(Filters.regex('^(🕒Now)$'),find_now), CommandHandler('terminate' , terminate) , MessageHandler(Filters.regex('^(ℹinfo)$') , info)],
    
    persistent=True,name='search_room_c_handler',allow_reentry=True)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(errorhandler.error_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


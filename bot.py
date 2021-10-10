import os
from os.path import join , dirname
from dotenv import load_dotenv
import telegram
from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.message import Message
from telegram.utils.helpers import UTC
from utils import free_classroom
from utils.free_classroom import find_free_room
from utils.find_classrooms import TIME_SHIFT
import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import (PicklePersistence,Updater,CommandHandler,CallbackQueryHandler,ConversationHandler,CallbackContext,MessageHandler , Filters, messagehandler)
from datetime import datetime ,date , timedelta
from telegram import ParseMode
import time
import sys
import pytz


MIN_TIME = 8
MAX_TIME = 20
logPath = "log/"


# Config Stuff

if not os.path.exists(logPath):
    os.mkdir(logPath)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("{0}{1}.log".format(logPath, str(time.time()))),
        logging.StreamHandler(sys.stdout)
    ]
)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

location_dict = {}
with open(join(dirname(__file__), 'json/location.json')) as location_json:
    location_dict = json.load(location_json)

texts = {}
with open(join(dirname(__file__), 'json/lang/en.json')) as text_json:
    texts = json.load(text_json)



TOKEN = os.environ.get("TOKEN")



# States for conversation handler
LOCATION , DAY , START_TIME , END_TIME, END , SETLOCPREF = range(6)
date_regex = '^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})$'
initial_keyboards = [["🔍Search" , "ℹinfo" ],["🕒Now"]]



# Helper functions for error messages and string builder


def bonk(update):
    update.message.reply_text(texts['error']) 
    update.message.reply_photo(photo = open(join(dirname(__file__), 'photos/bonk.jpg'),'rb'))    

def room_builder_str(available_rooms):
    splitted_msg = []
    available_rooms_str = ""
    for building in available_rooms:
        if  MAX_MESSAGE_LENGTH - len(available_rooms_str) <= 50:
            splitted_msg.append(available_rooms_str)
            available_rooms_str = ""
        available_rooms_str += '\n<b>{}</b>\n'.format(building)
        for room in available_rooms[building]:
            available_rooms_str += ' <a href ="{}">{}</a>\n'.format(room['link'],room['name'])
    splitted_msg.append(available_rooms_str)
    return splitted_msg



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

    if message not in location_dict:
        bonk(update)
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

    if message not in location_dict:
        bonk(update)
        return DAY
    
    context.user_data["location"] = message

    reply_keyboard = [[(datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
    update.message.reply_text(texts['day'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return START_TIME



def choose_start_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  choose start time state" , user.username)
    
    current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
    if message != 'Today' and message != 'Tomorrow':
        chosen_date = datetime.strptime(message, '%d/%m/%Y').date()
        print(current_date , chosen_date)
        if chosen_date < current_date or chosen_date > (current_date + timedelta(days=6)):
            bonk(update)
            return START_TIME
    else:
        message = current_date.strftime("%d/%m/%Y") if message == 'Today' else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
    context.user_data['date'] = message

    reply_keyboard = [[x] for x in range(MIN_TIME,MAX_TIME)]
    update.message.reply_text(texts['starting_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    
    return END_TIME



def choose_end_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  choose end time state" , user.username)
    start_time = 0
    #check if input is integer
    
    try:
        start_time = int(message)
    except Exception:
        bonk(update)
        return END_TIME
    
    #check if previous input is correct
    if start_time > MAX_TIME or start_time < MIN_TIME:
        bonk(update)
        return END_TIME

    context.user_data['start_time'] = start_time
    reply_keyboard = [[x] for x in range(start_time + 1 , MAX_TIME + 1)]
    update.message.reply_text(texts['ending_time'],reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True) )

    return END

def end_state(update: Update , context: CallbackContext) ->int:
    global location
    user = update.message.from_user
    message = update.message.text
    end_time = 0
    logging.info("%s in the end state" , user.username)

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    location = context.user_data['location']
    
    
    #check if input is integer
    try:
        end_time = int(message)
    except Exception:
        bonk(update)
        return END
    
    
    # check if previuos input is correct
    if int(start_time) >= end_time or end_time > MAX_TIME + 1:
        bonk(update)
        return END

    
    day , month , year = date.split('/')
    available_rooms = find_free_room(float(start_time + TIME_SHIFT) , float(end_time + TIME_SHIFT) , location_dict[location],int(day) , int(month) , int(year))  
    for m in room_builder_str(available_rooms):
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

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


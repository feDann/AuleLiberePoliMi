import os
import time
import sys
import pytz
import json
import logging
from os.path import join , dirname
from dotenv import load_dotenv
import telegram
from telegram.message import Message
from utils.free_classroom import find_free_room
from utils.find_classrooms import TIME_SHIFT , MAX_TIME , MIN_TIME
from telegram import  Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove
from telegram.ext import (PicklePersistence,Updater,CommandHandler,ConversationHandler,CallbackContext,MessageHandler , Filters)
from datetime import datetime , timedelta
from telegram import ParseMode
from functions import errorhandler , string_builder , input_check , keyboard_builder , user_data_handler


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



# States for conversation handler
INITIAL_STATE, SET_LOCATION , SET_DAY , SET_START_TIME ,  SET_END_AND_SEND , SETTINGS , SET_LANG = range(7)
date_regex = '^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})$'




# Functions to handle all the states

def start(update: Update , context: CallbackContext) ->int:
    
    lang = user_data_handler.initialize_user_data(context)     
    user = update.message.from_user
    initial_keyboard = keyboard_builder.initial_keyboard()
    logging.info("%s started conversation" , user.username)

    update.message.reply_text(texts[lang]['welcome'].format(user.username),disable_web_page_preview=True , parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))

    return INITIAL_STATE


def initial_state(update:Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in  choose initial state" , user.username)

    
    if message == "🔍Search":
        update.message.reply_text(texts[lang]['location'] , reply_markup=ReplyKeyboardMarkup(keyboard_builder.search_keyboard(location_dict ),one_time_keyboard=True))
        return SET_LOCATION
    elif message == "🕒Now":
        pass
    elif message == "⚙️Preferences":
        update.message.reply_text(texts[lang]["settings"],reply_markup=ReplyKeyboardMarkup(keyboard_builder.preference_keyboard()))
        return SETTINGS


def settings(update: Update , context : CallbackContext):
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  language settings" , user.username)
    lang = user_data_handler.get_lang(context)
    update.message.reply_text(texts[lang]["language"] , reply_markup=ReplyKeyboardMarkup(keyboard_builder.language_keyboard(texts)))
    return SET_LANG

def set_language(update: Update , context : CallbackContext):
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set language" , user.username)
    
    if not input_check.language_check(message , texts):
        errorhandler.bonk(update , texts , lang)
        return SET_LANG
    lang = message
    user_data_handler.update_lang(lang , context)
    
    update.message.reply_text(texts[lang]["settings"],reply_markup=ReplyKeyboardMarkup(keyboard_builder.preference_keyboard()))
    return SETTINGS
    


def set_location_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in  set location state" , user.username)

    if not input_check.location_check(message,location_dict):
        errorhandler.bonk(update )
        return SET_LOCATION
    
    context.user_data["location"] = message

    update.message.reply_text(texts[lang]['day'],reply_markup=ReplyKeyboardMarkup(keyboard_builder.day_keyboard() , one_time_keyboard=True) )

    return SET_DAY



def set_day_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set day state" , user.username)
    
    if input_check.day_check(message):
        current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
        message = current_date.strftime("%d/%m/%Y") if message == 'Today' else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        errorhandler.bonk(update)
        return SET_DAY

    context.user_data['date'] = message
    update.message.reply_text(texts[lang]['starting_time'],reply_markup=ReplyKeyboardMarkup(keyboard_builder.start_time_keyboard() , one_time_keyboard=True) )
    
    return SET_START_TIME



def set_start_time_state(update: Update , context: CallbackContext) ->int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set start state" , user.username)
    ret,start_time = input_check.start_time_check(message)
    
    if not ret:
        errorhandler.bonk(update )
        return SET_START_TIME

    context.user_data['start_time'] = start_time
    update.message.reply_text(texts[lang]['ending_time'],reply_markup=ReplyKeyboardMarkup(keyboard_builder.end_time_keyboard(start_time ,) , one_time_keyboard=True) )

    return SET_END_AND_SEND


def end_state(update: Update , context: CallbackContext) ->int:
    global location
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    initial_keyboard = keyboard_builder.initial_keyboard()

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    location = context.user_data['location']
    ret ,end_time = input_check.end_time_check(message ,start_time)

    if not ret:
        errorhandler.bonk(update )
        return SET_END_AND_SEND

    logging.info("%s in the set end time state and search" , user.username)
    
    day , month , year = date.split('/')
    available_rooms = find_free_room(float(start_time + TIME_SHIFT) , float(end_time + TIME_SHIFT) , location_dict[location],int(day) , int(month) , int(year))  
    for m in string_builder.room_builder_str(available_rooms):
        update.message.reply_chat_action(telegram.ChatAction.TYPING)
        update.message.reply_text(m,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    
    logging.info("%s search was: %s %s %d %d" , user.username , location , date , start_time , end_time )
    
    
    user_data_handler.reset_user_data(context)
    
    return INITIAL_STATE



# fallback funtions

def terminate(update: Update, context: CallbackContext) -> int:
    # terminate the conversation
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)

    logging.info("%s terminated the conversation.", user.username)
    update.message.reply_text(texts[lang]['terminate'], reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def info(update: Update, context: CallbackContext):
    user = update.message.from_user
    initial_keyboard = keyboard_builder.initial_keyboard()
    lang = user_data_handler.get_lang(context)
    logging.info("User %s asked for more info.", user.username)
    update.message.reply_text(texts[lang]['info'],parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return

def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    initial_keyboard = keyboard_builder.initial_keyboard()
    lang = user_data_handler.get_lang(context)
    logging.info("User %s canceled.", user.username)
    update.message.reply_text(texts[lang]['cancel'] ,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return INITIAL_STATE



# Create the bot and all the necessary handler


def main():
    #add persistence for states
    pp = PicklePersistence(filename='aulelibere_pp')

    updater = Updater(token=TOKEN , use_context=True , persistence=pp)
    dispatcher = updater.dispatcher
    

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            INITIAL_STATE : [MessageHandler(Filters.regex('^(🔍Search)$') | Filters.regex('^(🕒Now)$') | Filters.regex('^(⚙️Preferences)$'),initial_state)],
            SET_LOCATION : [MessageHandler(Filters.text & ~Filters.command,set_location_state)],
            SET_DAY : [MessageHandler(Filters.regex(date_regex) | Filters.regex('^(Today)$') | Filters.regex('^(Tomorrow)$'), set_day_state )],
            SET_START_TIME : [MessageHandler(Filters.text & ~Filters.command,set_start_time_state)],
            SET_END_AND_SEND : [MessageHandler(Filters.text & ~Filters.command, end_state)],
            SETTINGS : [MessageHandler(Filters.regex('^(Language)$') , settings)],
            SET_LANG : [MessageHandler(Filters.text & ~Filters.command , set_language)]
            },
        fallbacks=[CommandHandler('terminate' , terminate) , MessageHandler(Filters.regex('^(ℹinfo)$') , info), CommandHandler("Cancel" , cancel)],
    
    persistent=True,name='search_room_c_handler',allow_reentry=True)

    dispatcher.add_error_handler(errorhandler.error_handler)
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


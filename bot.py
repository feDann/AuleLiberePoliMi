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
from telegram.ext import (PicklePersistence,Updater,CommandHandler,ConversationHandler,CallbackContext,MessageHandler , Filters , CallbackQueryHandler)
from datetime import datetime , timedelta
from telegram import ParseMode
from functions import errorhandler , string_builder , input_check , keyboard_builder , user_data_handler ,regex_builder


LOGPATH = "log/"
DIRPATH = dirname(__file__)



"""
Create a dir for the logs file
"""
if not os.path.exists(LOGPATH):
    os.mkdir(LOGPATH)

"""
Basic logger config
"""
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




"""
Code below load all the query params for the campus in a dict
"""
location_dict = {}
with open(join(DIRPATH, 'json/location.json')) as location_json:
    location_dict = json.load(location_json)

"""
Code below load in a dict all the text messages in all the available languages
"""
texts = {}
for lang in os.listdir(join(DIRPATH , 'json/lang')):
    with open(join(DIRPATH,'json' , 'lang' , lang) , 'r') as f:
        texts[lang[:2]] = json.load(f)

"""
The fragment of code below load in a dict all the aliases for the various commands
eg for search: Search, Cerca ecc
"""
command_keys = {}
for lang in texts:
    for key in texts[lang]["keyboards"]:
        if key not in command_keys:
            command_keys[key] = []
        command_keys[key].append(texts[lang]["keyboards"][key])

KEYBOARDS = keyboard_builder.KeyboadBuilder(texts , location_dict)

TOKEN = os.environ.get("TOKEN")



"""
States for the conversation handler
"""
INITIAL_STATE, SET_LOCATION , SET_DAY , SET_START_TIME ,  SET_END_AND_SEND , SETTINGS , SET_LANG , SET_CAMPUS , SET_TIME , NOW= range(10)



"""
The Functions below are used for the various commands in the states, first three functions are
referred to the initial state, second three are referred to the settings state
"""

def search(update: Update , context : CallbackContext , lang) -> int:
    """
    Send the keyboard for the location and return to set_location state ,
    this function is the initial state for the searching process
    """
    update.message.reply_text(texts[lang]["texts"]['location'] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang),one_time_keyboard=True))
    return SET_LOCATION


def now(update: Update , context : CallbackContext, lang) -> int:
    """
    Thhis functions implements the quick search, after checking if the campus is in
    the preferences of the user call the end_state function, otherwise return to the initial_state
    """
    user = update.message.from_user
    logging.info("%s in now state" , user.username)
    loc, dur = user_data_handler.get_user_preferences(context)

    if loc is None:
        update.message.reply_text(texts[lang]["texts"]["missing"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.initial_keyboard(lang)))
        return INITIAL_STATE
    
    start_time = int(datetime.now(pytz.timezone('Europe/Rome')).strftime('%H'))
    if start_time > MAX_TIME or start_time < MIN_TIME:
        update.message.reply_text(texts[lang]["texts"]['ops'])
        start_time = MIN_TIME
    end_time = start_time + dur
    context.user_data["location"] = loc   
    context.user_data["date"] = datetime.now(pytz.timezone('Europe/Rome')).strftime("%d/%m/%Y")
    context.user_data["start_time"] = start_time
    update.message.text = end_time
    return end_state(update, context)


def preferences(update: Update , context : CallbackContext, lang) -> int:
    """
    Send the keyboard for the preferences state and return to setting state
    """
    update.message.reply_text(texts[lang]["texts"]["settings"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

def language(update: Update , context : CallbackContext, lang) -> int:
    """
    Send the keyboard for the languages and return to set_lang state
    """
    update.message.reply_text(texts[lang]["texts"]["language"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.language_keyboard(lang)))
    return SET_LANG


def duration(update: Update , context : CallbackContext, lang) -> int:
    """
    Send the keyboard for the duration and return to set_time state
    """
    update.message.reply_text(texts[lang]["texts"]["time"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.time_keyboard()))
    return SET_TIME


def campus(update: Update , context : CallbackContext, lang) -> int:
    """
    Send the keyboard for the campus and return to set_campus state
    """
    update.message.reply_text(texts[lang]["texts"]["campus"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang)))
    return SET_CAMPUS

"""
Code below map in a dict all the aliases for a certain function,
e.g. map all the aliases of search (search, cerca, ecc) to the search function
"""
function_map = {}
function_mapping = {"search" : search , "now" : now , "preferences" : preferences , "language" : language , "time" : duration, "campus" : campus}
for key in command_keys:
    if key in function_mapping:
        for alias in command_keys[key]:
            function_map[alias] = function_mapping[key]



"""STATES FUNCTIONS"""

def start(update: Update , context: CallbackContext) ->int:
    """
    Start function for the conversation handler, initialize the dict of user_data
    in the context and return to the initial state
    """
    lang = user_data_handler.initialize_user_data(context)     
    user = update.message.from_user
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    logging.info("%s started conversation" , user.username)

    update.message.reply_text(texts[lang]["texts"]['welcome'].format(user.username),disable_web_page_preview=True , parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))

    return INITIAL_STATE


def initial_state(update:Update , context: CallbackContext) ->int:
    """
    Initial State of the ConversationHandler, through the function_map return to
    the right function based on the user input
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in  choose initial state" , user.username)
    
    return function_map[message](update,context,lang)



def settings(update: Update , context : CallbackContext):
    """
    Settings state of the Conversation Handler, from here based on the user input
    calls the right function using the function_map 
    """
    user = update.message.from_user
    message = update.message.text
    logging.info("%s in  settings" , user.username)
    lang = user_data_handler.get_lang(context)
    
    return function_map[message](update,context,lang)

def set_language(update: Update , context : CallbackContext):
    """
    In this state is stored in the user_data the preference for the language,
    if the input check goes well it returns to the settings, otherwise remain 
    in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set language" , user.username)
    
    if not input_check.language_check(message , texts):
        errorhandler.bonk(update , texts , lang)
        return SET_LANG
    lang = message
    user_data_handler.update_lang(lang , context)
    
    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS
    
def set_campus(update: Update , context: CallbackContext):
    """
    In this state is stored in the user_data the preference for the campus,
    if the input check goes well it returns to the settings, otherwise remain
    in the same state  
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set campus" , user.username)

    if not input_check.location_check(message , location_dict):
        errorhandler.bonk(update , texts , lang)
        return SET_CAMPUS

    user_data_handler.update_campus(message , context)
    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

def set_time(update: Update , context: CallbackContext):
    """
    In this state is stored in the user_data the preference for the duration
    in terms of hours for the quick search, if the input check goes well it 
    returns to the settings, otherwise remain in the same state   
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set time" , user.username)
    
    if not input_check.time_check(message):
        errorhandler.bonk(update , texts , lang)
        return SET_TIME

    user_data_handler.update_time(message , context)
    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS


def set_location_state(update: Update , context: CallbackContext) ->int:
    """
    In this state is saved in the user_data the location for the search process,
    if the input check goes well it returns to the set_day, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in  set location state" , user.username)

    if not input_check.location_check(message,location_dict):
        errorhandler.bonk(update ,texts , lang )
        return SET_LOCATION
    
    context.user_data["location"] = message

    update.message.reply_text(texts[lang]["texts"]['day'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.day_keyboard(lang) , one_time_keyboard=True) )

    return SET_DAY



def set_day_state(update: Update , context: CallbackContext) ->int:
    """
    In this state is saved in the user_data the chosen day for the search process,
    if the input check goes well it returns to the set_start_time, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set day state" , user.username)
    
    if input_check.day_check(message ,texts , lang):
        current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
        message = current_date.strftime("%d/%m/%Y") if message == texts[lang]["keyboards"]["today"] else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        errorhandler.bonk(update , texts , lang)
        return SET_DAY

    context.user_data['date'] = message
    update.message.reply_text(texts[lang]["texts"]['starting_time'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.start_time_keyboard(lang) , one_time_keyboard=True) )
    
    return SET_START_TIME



def set_start_time_state(update: Update , context: CallbackContext) ->int:
    """
    In this state is saved in the user_data the starting time of the search process,
    if the input check goes well it returns to the end_state, otherwise remain in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%s in set start state" , user.username)
    ret,start_time = input_check.start_time_check(message)
    
    if not ret:
        errorhandler.bonk(update , texts , lang )
        return SET_START_TIME

    context.user_data['start_time'] = start_time
    update.message.reply_text(texts[lang]["texts"]['ending_time'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.end_time_keyboard(lang ,start_time ) , one_time_keyboard=True) )

    return SET_END_AND_SEND


def end_state(update: Update , context: CallbackContext) ->int:
    """
    Final state of the search process, check if the last input is valid and 
    proceed to return to the user all the free classrooms, otherwise remains
    in the same state
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    location = context.user_data['location']
    ret ,end_time = input_check.end_time_check(message ,start_time)

    if not ret:
        errorhandler.bonk(update , texts , lang )
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



"""FALLBACKS"""

def terminate(update: Update, context: CallbackContext) -> int:
    """
    This function terminate the Conversation handler
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)

    logging.info("%s terminated the conversation.", user.username)
    update.message.reply_text(texts[lang]["texts"]['terminate'], reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def info(update: Update, context: CallbackContext):
    """
    Return some info to the user
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    logging.info("User %s asked for more info.", user.username)
    update.message.reply_text(texts[lang]["texts"]['info'],parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return

def cancel(update: Update, context: CallbackContext):
    """
    Stop any process and return to the initial state
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    logging.info("User %s canceled.", user.username)
    update.message.reply_text(texts[lang]["texts"]['cancel'] ,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return INITIAL_STATE




"""BOT INITIALIZATION"""

def main():
    #add persistence for states
    pp = PicklePersistence(filename='aulelibere_pp')
    
    regex = regex_builder.RegexBuilder(texts)

    updater = Updater(token=TOKEN , use_context=True , persistence=pp)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            INITIAL_STATE : [MessageHandler(Filters.regex(regex.initial_state()),initial_state)],
            SET_LOCATION : [MessageHandler(Filters.text & ~Filters.command,set_location_state)],
            SET_DAY : [MessageHandler(Filters.regex(regex.date_regex()) | Filters.regex(regex.date_string_regex()), set_day_state )],
            SET_START_TIME : [MessageHandler(Filters.text & ~Filters.command,set_start_time_state)],
            SET_END_AND_SEND : [MessageHandler(Filters.text & ~Filters.command, end_state)],
            SETTINGS : [MessageHandler(Filters.regex(regex.settings_regex()) , settings)],
            SET_LANG : [MessageHandler(Filters.text & ~Filters.command , set_language)],
            SET_CAMPUS: [MessageHandler(Filters.text & ~Filters.command , set_campus)],
            SET_TIME: [MessageHandler(Filters.text & ~Filters.command , set_time)]
            },
        fallbacks=[CommandHandler('terminate' , terminate)  , MessageHandler(Filters.regex(regex.info_regex()) , info), MessageHandler(Filters.regex(regex.cancel_command()), cancel)],
    
    persistent=True,name='search_room_c_handler',allow_reentry=True)

    dispatcher.add_error_handler(errorhandler.error_handler)
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


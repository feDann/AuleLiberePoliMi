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
from search.free_classroom import find_free_room
from search.find_classrooms import TIME_SHIFT , MAX_TIME , MIN_TIME
from telegram import  Update , ReplyKeyboardMarkup ,ReplyKeyboardRemove , InlineQueryResultArticle , InputTextMessageContent
from telegram.ext import (PicklePersistence,Updater,CommandHandler,ConversationHandler,CallbackContext,MessageHandler , Filters , CallbackQueryHandler , InlineQueryHandler)
from datetime import datetime , timedelta
from telegram import ParseMode
from functions import errorhandler , string_builder , input_check , keyboard_builder , user_data_handler ,regex_builder , analytics


LOGPATH = "log/"
DIRPATH = dirname(__file__)



"""
Create a directory for log files if it doesn't exist.
"""
if not os.path.exists(LOGPATH):
    os.mkdir(LOGPATH)

"""
Configure the basic logging settings.
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("{0}{1}.log".format(LOGPATH, str(time.time()))),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

dotenv_path = join(DIRPATH, '.env')
load_dotenv(dotenv_path)




"""
Load all campus location query parameters into a dictionary.
"""
location_dict = {}
with open(join(DIRPATH, 'json/location.json')) as location_json:
    location_dict = json.load(location_json)

"""
Load all text messages for available languages into a dictionary.
"""
texts = {}
for lang in os.listdir(join(DIRPATH , 'json/lang')):
    with open(join(DIRPATH,'json' , 'lang' , lang) , 'r') as f:
        texts[lang[:2]] = json.load(f)

"""
Map command aliases (e.g., Search, Cerca) to their canonical keys.
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
States for the conversation handler.
"""
INITIAL_STATE = 0
SET_CAMPUS_SELECTION = 1   # prima scelta: elenco campus
SET_SUBLOCATION = 2        # seconda scelta: elenco sotto-sedi per il campus scelto
SET_DAY = 3
SET_START_TIME = 4
SET_END_AND_SEND = 5
SETTINGS = 6
SET_LANG = 7
SET_CAMPUS = 8   # usato nelle settings per impostare il campus preferito
SET_TIME = 9
NOW = 10



"""
Handler functions for conversation states.
The first group corresponds to the initial state, while the second group handles settings.
"""

def search(update: Update , context : CallbackContext , lang) -> int:
    """Initiates the search process by showing the list of campuses.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SET_CAMPUS_SELECTION).
    """
    update.message.reply_text(texts[lang]["texts"]['location'] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang),one_time_keyboard=True))
    return SET_CAMPUS_SELECTION


def now(update: Update , context : CallbackContext, lang) -> int:
    """Performs a quick search based on user preferences.

    If preferences are set, proceeds to the end state. Otherwise, prompts the user
    to set preferences.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (END_STATE or INITIAL_STATE).
    """
    user = update.message.from_user
    logging.info("%d : %s in now state" , user.id ,  user.username)
    loc, dur = user_data_handler.get_user_preferences(context)

    if loc is None:
        update.message.reply_text(texts[lang]["texts"]["missing"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.initial_keyboard(lang)))
        return INITIAL_STATE

    start_time = int(datetime.now(pytz.timezone('Europe/Rome')).strftime('%H'))
    if start_time >= MAX_TIME or start_time < MIN_TIME:
        update.message.reply_text(texts[lang]["texts"]['ops'])
        start_time = MIN_TIME
    end_time = start_time + dur if start_time + dur < MAX_TIME else MAX_TIME

    if loc in location_dict:
        context.user_data["location"] = location_dict[loc]["code"]
        context.user_data["location_name"] = loc
    else:
        # Fallback if somehow invalid
        context.user_data["location"] = loc
        context.user_data["location_name"] = loc

    context.user_data["date"] = datetime.now(pytz.timezone('Europe/Rome')).strftime("%d/%m/%Y")
    context.user_data["start_time"] = start_time
    update.message.text = str(end_time)
    return end_state(update, context)


def preferences(update: Update , context : CallbackContext, lang) -> int:
    """Displays the preferences menu.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SETTINGS).
    """
    update.message.reply_text(texts[lang]["texts"]["settings"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

def language(update: Update , context : CallbackContext, lang) -> int:
    """Displays the language selection menu.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SET_LANG).
    """
    update.message.reply_text(texts[lang]["texts"]["language"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.language_keyboard(lang)))
    return SET_LANG


def duration(update: Update , context : CallbackContext, lang) -> int:
    """Displays the duration selection menu for quick search.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SET_TIME).
    """
    update.message.reply_text(texts[lang]["texts"]["time"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.time_keyboard(lang)))
    return SET_TIME


def campus(update: Update , context : CallbackContext, lang) -> int:
    """Displays the campus selection menu for preferences.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SET_CAMPUS).
    """
    update.message.reply_text(texts[lang]["texts"]["campus"] , reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang)))
    return SET_CAMPUS

def set_format(update: Update, context: CallbackContext, lang):
    """Toggles between text and emoji display formats.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
        lang (str): The language code.

    Returns:
        int: The next state (SETTINGS).
    """
    current_mode = user_data_handler.get_format_mode(context)
    new_mode = 'emoji' if current_mode == 'text' else 'text'
    
    user_data_handler.update_format(new_mode, context)
    
    msg_key = "format_emoji" if new_mode == 'emoji' else "format_text"
    update.message.reply_text(texts[lang]["texts"][msg_key], reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

"""
Map aliased commands (e.g., 'search', 'cerca') to their corresponding functions.
"""
function_map = {}
function_mapping = {"search" : search , "now" : now , "preferences" : preferences , "language" : language , "time" : duration, "campus" : campus, "format": set_format}
for key in command_keys:
    if key in function_mapping:
        for alias in command_keys[key]:
            function_map[alias] = function_mapping[key]

"""STATES FUNCTIONS"""

def start(update: Update , context: CallbackContext) ->int:
    """Starts the conversation and initializes user data.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The initial state (INITIAL_STATE).
    """
    lang = user_data_handler.initialize_user_data(context)
    user = update.message.from_user
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    analytics.track(user.id, user.username)
    logging.info("%s started conversation" , user.username)

    update.message.reply_text(texts[lang]["texts"]['welcome'].format(user.username),disable_web_page_preview=True , parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))

    return INITIAL_STATE


def initial_state(update:Update , context: CallbackContext) ->int:
    """Handles parsing of the initial state input.

    Calls the appropriate function based on the user's text message.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state returned by the called function.
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in  choose initial state" , user.id , user.username)

    return function_map[message](update,context,lang)



def settings(update: Update , context : CallbackContext):
    """Handles parsing of the settings state input.

    Calls the appropriate settings function based on user input.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state returned by the called function.
    """
    user = update.message.from_user
    message = update.message.text
    logging.info("%d : %s in  settings" , user.id , user.username)
    lang = user_data_handler.get_lang(context)

    return function_map[message](update,context,lang)

def set_language(update: Update , context: CallbackContext):
    """Sets the user's preferred language.

    Validates the input and updates the user data.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (SETTINGS or SET_LANG on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set language" ,user.id , user.username)

    if not input_check.language_check(message , texts):
        errorhandler.bonk(update , texts , lang)
        return SET_LANG
    lang = message
    user_data_handler.update_lang(lang , context)

    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

def set_campus(update: Update , context: CallbackContext):
    """Sets the user's preferred campus.

    Validates the input and updates the user data.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (SETTINGS or SET_CAMPUS on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set campus" ,user.id , user.username)

    if not input_check.location_check(message , location_dict):
        errorhandler.bonk(update , texts , lang)
        return SET_CAMPUS

    user_data_handler.update_campus(message , context)
    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS

def set_time(update: Update , context: CallbackContext):
    """Sets the user's preferred duration for quick search.

    Validates the input and updates the user data.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (SETTINGS or SET_TIME on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set time" ,user.id ,  user.username)

    if not input_check.time_check(message):
        errorhandler.bonk(update , texts , lang)
        return SET_TIME

    user_data_handler.update_time(message , context)
    update.message.reply_text(texts[lang]["texts"]["success"],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.preference_keyboard(lang)))
    return SETTINGS




# def set_location_state(update: Update , context: CallbackContext) ->int:
#     """
#     Legacy: single-step location selection (kept for compatibility)
#     """
#     user = update.message.from_user
#     message = update.message.text
#     lang = user_data_handler.get_lang(context)
#     logging.info("%d : %s in  set location state" ,user.id , user.username)
# 
#     if not input_check.location_check(message,location_dict):
#         errorhandler.bonk(update ,texts , lang )
#         return SET_LOCATION
# 
#     context.user_data["location"] = message
# 
#     update.message.reply_text(texts[lang]["texts"]['day'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.day_keyboard(lang) , one_time_keyboard=True) )
# 
#     return SET_DAY


def set_campus_selection_state(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set campus selection", user.id, user.username)

    # selezionato un campus (chiave top-level)
    if message in location_dict:
        context.user_data["selected_campus_for_sedi"] = message
        update.message.reply_text(
            texts[lang]["texts"]["location"],
            reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang, campus=message), one_time_keyboard=True)
        )
        return SET_SUBLOCATION

    # selezionata direttamente una sede (cerca in tutte le sedi)
    for campus, data in location_dict.items():
        sedi = data.get("sedi", {}) if isinstance(data, dict) else {}
        if message in sedi:
            context.user_data["location"] = message
            update.message.reply_text(texts[lang]["texts"]['day'],
                                      reply_markup=ReplyKeyboardMarkup(KEYBOARDS.day_keyboard(lang), one_time_keyboard=True))
            return SET_DAY

    errorhandler.bonk(update, texts, lang)
    return SET_CAMPUS_SELECTION


def set_sublocation_state(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set sublocation", user.id, user.username)

    cancel_label = texts[lang]["keyboards"]["cancel"]
    all_label = texts[lang]["keyboards"]["all_buildings"]

    # Indietro / annulla -> torna alla lista campus
    if message == cancel_label:
        update.message.reply_text(
            texts[lang]["texts"]['location'],
            reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang), one_time_keyboard=True)
        )
        return SET_CAMPUS_SELECTION

    # "Tutti gli edifici" -> seleziona l'intero campus
    is_all_buildings = False
    for l in texts:
        if message == texts[l]["keyboards"]["all_buildings"]:
            is_all_buildings = True
            break

    if is_all_buildings:
        campus = context.user_data.get("selected_campus_for_sedi")
        if campus and campus in location_dict:
            # Save the CAMPUS CODE (e.g. MIA)
            context.user_data["location"] = location_dict[campus]["code"]
            # Save the NAME for display
            context.user_data["location_name"] = campus
            update.message.reply_text(texts[lang]["texts"]['day'],
                                      reply_markup=ReplyKeyboardMarkup(KEYBOARDS.day_keyboard(lang), one_time_keyboard=True))
            return SET_DAY
        # se manca il campus salvato, torna all'elenco campus
        update.message.reply_text(texts[lang]["texts"]['location'],
                                  reply_markup=ReplyKeyboardMarkup(KEYBOARDS.location_keyboard(lang), one_time_keyboard=True))
        return SET_CAMPUS_SELECTION

    # scelta di una singola sede
    # We need to find which campus contains this sede
    selected_campus = context.user_data.get("selected_campus_for_sedi")
    if selected_campus and selected_campus in location_dict:
         data = location_dict[selected_campus]
         sedi = data.get("sedi", {}) if isinstance(data, dict) else {}
         if message in sedi:
             # Save the SEDE CODE (e.g. MIA02)
             context.user_data["location"] = sedi[message]
             context.user_data["location_name"] = message
             update.message.reply_text(texts[lang]["texts"]['day'],
                                       reply_markup=ReplyKeyboardMarkup(KEYBOARDS.day_keyboard(lang), one_time_keyboard=True))
             return SET_DAY

    errorhandler.bonk(update, texts, lang)
    return SET_SUBLOCATION
def set_day_state(update: Update , context: CallbackContext) ->int:
    """Sets the date for the search.

    Validates the date input and prompts for the start time.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (SET_START_TIME or SET_DAY on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set day state" ,user.id , user.username)

    ret , chosen_date = input_check.day_check(message ,texts , lang)
    if not ret:
        errorhandler.bonk(update , texts , lang)
        return SET_DAY

    context.user_data['date'] = chosen_date
    update.message.reply_text(texts[lang]["texts"]['starting_time'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.start_time_keyboard(lang) , one_time_keyboard=True) )

    return SET_START_TIME



def set_start_time_state(update: Update , context: CallbackContext) ->int:
    """Sets the starting time for the search.

    Validates the time input and prompts for the end time.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (SET_END_AND_SEND or SET_START_TIME on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    logging.info("%d : %s in set start state" ,user.id , user.username)
    ret,start_time = input_check.start_time_check(message)

    if not ret:
        errorhandler.bonk(update , texts , lang )
        return SET_START_TIME

    context.user_data['start_time'] = start_time
    update.message.reply_text(texts[lang]["texts"]['ending_time'],reply_markup=ReplyKeyboardMarkup(KEYBOARDS.end_time_keyboard(lang ,start_time ) , one_time_keyboard=True) )

    return SET_END_AND_SEND


def end_state(update: Update , context: CallbackContext) ->int:
    """Executes the room search and displays results.

    Validates the end time, performs the search using `find_free_room`, and sends
    the results to the user.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The next state (INITIAL_STATE or SET_END_AND_SEND on error).
    """
    user = update.message.from_user
    message = update.message.text
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    format_mode = user_data_handler.get_format_mode(context)

    start_time = context.user_data['start_time']
    date = context.user_data['date']
    location = context.user_data['location']
    location_name = context.user_data.get('location_name', location) # Fallback to code if name missing
    
    ret ,end_time = input_check.end_time_check(message ,start_time)

    if not ret:
        errorhandler.bonk(update , texts , lang )
        return SET_END_AND_SEND

    logging.info("%d : %s in the set end time state and search" ,user.id , user.username)

    day , month , year = date.split('/')
    try:
        update.message.reply_text(texts[lang]["texts"]["loading"])
        # Pass location code directly
        available_rooms = find_free_room(float(start_time + TIME_SHIFT) , float(end_time + TIME_SHIFT) , location, int(day) , int(month) , int(year))
        
        # Friendly Header
        header = f"📅 <b>{date}</b>\n📍 <b>{location_name}</b>\n⏰ <b>{start_time}:00 - {end_time}:00</b>"
        update.message.reply_text(header, parse_mode=ParseMode.HTML)
        
        if not available_rooms:
             update.message.reply_text(texts[lang]["texts"]["no_rooms"])
        else:
            for m in string_builder.room_builder_str(available_rooms , texts[lang]["texts"], format_mode):
                update.message.reply_chat_action(telegram.ChatAction.TYPING)
                update.message.reply_text(m,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))

        logging.info("%d : %s search was: %s %s %d %d" , user.id , user.username , location , date , start_time , end_time )
    except Exception as e:
        logging.error("Exception occurred during find_free_room: %s", e)
        logging.info("Search context: %s  %s  %d-%d " , date , location , start_time , end_time)
        update.message.reply_text(texts[lang]["texts"]["exception"] ,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard) ,disable_web_page_preview=True)


    user_data_handler.reset_user_data(context)

    return INITIAL_STATE



"""FALLBACKS"""

def terminate(update: Update, context: CallbackContext) -> int:
    """Terminates the conversation.

    Clears user data and ends the conversation handler.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: ConversationHandler.END
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    context.user_data.clear()

    logging.info("%d : %s terminated the conversation.", user.id , user.username)
    update.message.reply_text(texts[lang]["texts"]['terminate'], reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def info(update: Update, context: CallbackContext):
    """Sends information about the bot to the user.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    logging.info("%d : %s asked for more info.", user.id , user.username)
    update.message.reply_text(texts[lang]["texts"]['info'],parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return

def cancel(update: Update, context: CallbackContext):
    """Cancels the current operation and returns to the initial state.

    Args:
        update (Update): The Telegram update object.
        context (CallbackContext): The callback context.

    Returns:
        int: The initial state (INITIAL_STATE).
    """
    user = update.message.from_user
    lang = user_data_handler.get_lang(context)
    initial_keyboard = KEYBOARDS.initial_keyboard(lang)
    user_data_handler.reset_user_data(context)
    logging.info("%d : %s canceled.", user.id , user.username)
    update.message.reply_text(texts[lang]["texts"]['cancel'] ,parse_mode=ParseMode.HTML , reply_markup=ReplyKeyboardMarkup(initial_keyboard))
    return INITIAL_STATE




def inline_query_handler(update: Update, context: CallbackContext):
    """Handles inline queries: runs the 'Now' search using saved user preferences."""
    user = update.inline_query.from_user
    lang = user_data_handler.get_lang(context)
    format_mode = user_data_handler.get_format_mode(context)
    loc, dur = user_data_handler.get_user_preferences(context)

    analytics.track(user.id, user.username)
    logging.info("%d : %s inline query", user.id, user.username)

    if loc is None:
        result = InlineQueryResultArticle(
            id="no_prefs",
            title="⚠️ No campus preference set",
            description="Open the bot and set your campus in Preferences first",
            input_message_content=InputTextMessageContent(texts[lang]["texts"]["missing"])
        )
        update.inline_query.answer([result], cache_time=0)
        return

    start_time = int(datetime.now(pytz.timezone('Europe/Rome')).strftime('%H'))
    if start_time >= MAX_TIME or start_time < MIN_TIME:
        start_time = MIN_TIME
    end_time = start_time + dur if start_time + dur < MAX_TIME else MAX_TIME

    if loc in location_dict:
        location_code = location_dict[loc]["code"]
        location_name = loc
    else:
        location_code = loc
        location_name = loc

    now_date = datetime.now(pytz.timezone('Europe/Rome'))
    date_str = now_date.strftime("%d/%m/%Y")

    try:
        available_rooms = find_free_room(
            float(start_time + TIME_SHIFT),
            float(end_time + TIME_SHIFT),
            location_code,
            now_date.day,
            now_date.month,
            now_date.year
        )

        header = f"📅 <b>{date_str}</b>\n📍 <b>{location_name}</b>\n⏰ <b>{start_time}:00 - {end_time}:00</b>"

        if not available_rooms:
            no_rooms_msg = header + "\n\n" + texts[lang]["texts"]["no_rooms"]
            result = InlineQueryResultArticle(
                id="no_rooms",
                title=f"🏫 {location_name} — {start_time}:00/{end_time}:00",
                description=texts[lang]["texts"]["no_rooms"],
                input_message_content=InputTextMessageContent(no_rooms_msg, parse_mode=ParseMode.HTML)
            )
            update.inline_query.answer([result], cache_time=0)
            return

        buildings = string_builder.building_builder_str(available_rooms, texts[lang]["texts"], format_mode)
        results = []
        for building_name, building_str in buildings:
            full_msg = header + building_str
            results.append(InlineQueryResultArticle(
                id=f"building_{building_name}",
                title=f"🏫 {building_name}",
                description=f"{location_name} | {start_time}:00 - {end_time}:00 | {date_str}",
                input_message_content=InputTextMessageContent(full_msg, parse_mode=ParseMode.HTML)
            ))

        update.inline_query.answer(results, cache_time=0)

    except Exception as e:
        logging.error("Inline query error: %s", e)
        result = InlineQueryResultArticle(
            id="error",
            title="❌ Error during search",
            input_message_content=InputTextMessageContent(
                texts[lang]["texts"]["exception"], parse_mode=ParseMode.HTML
            )
        )
        update.inline_query.answer([result], cache_time=0)


"""BOT INITIALIZATION"""

DATAPATH = "data/"
if not os.path.exists(DATAPATH):
    os.mkdir(DATAPATH)

analytics.init(DATAPATH)

def main():
    #add persistence for states
    pp = PicklePersistence(filename=join(DATAPATH, 'aulelibere_pp'))

    regex = regex_builder.RegexBuilder(texts)

    updater = Updater(token=TOKEN , use_context=True , persistence=pp)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            INITIAL_STATE : [MessageHandler(Filters.regex(regex.initial_state()),initial_state)],
            SET_CAMPUS_SELECTION : [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()),set_campus_selection_state)],
            SET_SUBLOCATION : [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()),set_sublocation_state)],
            SET_DAY : [MessageHandler(Filters.regex(regex.date_regex()) | Filters.regex(regex.date_string_regex()), set_day_state )],
            SET_START_TIME : [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()),set_start_time_state)],
            SET_END_AND_SEND : [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()), end_state)],
            SETTINGS : [MessageHandler(Filters.regex(regex.settings_regex()) , settings)],
            SET_LANG : [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()) , set_language)],
            SET_CAMPUS: [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()) , set_campus)],
            SET_TIME: [MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(regex.cancel_command()) , set_time)]
            },
        fallbacks=[CommandHandler('terminate' , terminate)  , MessageHandler(Filters.regex(regex.info_regex()) , info), MessageHandler(Filters.regex(regex.cancel_command()), cancel)],

    persistent=True,name='search_room_c_handler',allow_reentry=True)

    dispatcher.add_error_handler(errorhandler.error_handler)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(InlineQueryHandler(inline_query_handler))

    # Heartbeat job
    def heartbeat(context: CallbackContext):
        logging.info("heartbeat")
        with open("heartbeat", "w") as f:
            f.write(str(time.time()))

    updater.job_queue.run_repeating(heartbeat, interval=30, first=1)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
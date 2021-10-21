from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

def get_lang(context:CallbackContext):
    """
    Return the language preference of the user
    """
    lang = '' 
    try:
        lang = context.user_data['preference']['lang']
    except Exception as e :
        lang = 'en' #Default Language
    return lang


def initialize_user_data(context: CallbackContext):
    """
    Initialize the user_data and set as default language english, and as default time 2 hours
    """
    context.user_data.clear()
    lang = 'en' # Default language    
    context.user_data['preference'] = {} # set the default language
    context.user_data['preference']['lang'] = lang
    context.user_data['preference']['time'] = 2

    return lang


def reset_user_data(context: CallbackContext):
    """
    reset all user_data referred to a search and keep all the preferences
    """
    if 'preference' in context.user_data:
        # Delete the search selection
        preference = context.user_data['preference']
        context.user_data.clear()
        context.user_data['preference'] = preference
    else:
        context.user_data.clear()
        initialize_user_data(context)


def update_lang(lang , context:CallbackContext):
    """
    update the language preference
    """
    context.user_data['preference']['lang'] = lang

def update_campus(campus , context:CallbackContext):
    """
    update the campus preference
    """
    context.user_data['preference']['campus'] = campus

def update_time(time , context:CallbackContext):
    """
    update the time preference
    """
    context.user_data['preference']['time'] = int(time)

def get_user_preferences(context:CallbackContext):
    """
    return a tuple of location , time that represent the preferred campus and time
    duration for the quick search
    """
    time = 0
    loc = None
    try:
        time = context.user_data["preference"]["time"]
    except Exception:
        pass
    try:
        loc = context.user_data["preference"]["campus"]
    except Exception:
        pass
    
    return loc , time
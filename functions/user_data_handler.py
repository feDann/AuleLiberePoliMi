import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

def get_lang(context:CallbackContext):
    lang = '' 
    try:
        lang = context.user_data['preference']['lang']
    except Exception as e :
        lang = 'en' #Default Language
    return lang


def initialize_user_data(context: CallbackContext):
    context.user_data.clear()
    lang = 'en' # Default language    
    context.user_data['preference'] = {} # set the default language
    context.user_data['preference']['lang'] = lang
    return lang


def reset_user_data(context: CallbackContext):
    if 'preference' in context.user_data:
        # Delete the search selection
        preference = context.user_data['preference']
        context.user_data.clear()
        context.user_data['preference'] = preference
    else:
        context.user_data.clear()
        initialize_user_data(context)
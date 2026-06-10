from telegram.ext import  CallbackContext

def get_lang(context:CallbackContext):
    """Retrieves the user's language preference.

    Args:
        context (CallbackContext): The context object containing user data.

    Returns:
        str: The language code (e.g., 'en', 'it'). Defaults to 'en' if not found.
    """
    lang = '' 
    try:
        lang = context.user_data['preference']['lang']
    except Exception as e :
        lang = 'en' #Default Language
    return lang


def initialize_user_data(context: CallbackContext):
    """Initializes user data with default preferences if not present.

    Sets default language to English, time to 2 hours, and format to 'text'.

    Args:
        context (CallbackContext): The context object containing user data.

    Returns:
        str: The current (or newly set) language content.
    """
    if "preference" not in context.user_data:
        context.user_data.clear()
        lang = 'en' # Default language    
        context.user_data['preference'] = {} # set the default language
        context.user_data['preference']['lang'] = lang
        context.user_data['preference']['time'] = 2
        context.user_data['preference']['format'] = 'text'

    return get_lang(context)


def reset_user_data(context: CallbackContext):
    """Resets user data related to search while preserving preferences.

    Args:
        context (CallbackContext): The context object containing user data.
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
    """Updates the user's language preference.

    Args:
        lang (str): The new language code.
        context (CallbackContext): The context object containing user data.
    """
    if  "preference" not in context.user_data:
        reset_user_data(context)
    context.user_data['preference']['lang'] = lang

def update_campus(campus , context:CallbackContext):
    """Updates the user's campus preference.

    Args:
        campus (str): The new campus identifier.
        context (CallbackContext): The context object containing user data.
    """
    if  "preference" not in context.user_data:
        reset_user_data(context)
    context.user_data['preference']['campus'] = campus

def update_time(time , context:CallbackContext):
    """Updates the user's quick search time duration preference.

    Args:
        time (int or str): The new duration in hours.
        context (CallbackContext): The context object containing user data.
    """
    if  "preference" not in context.user_data:
        reset_user_data(context)
    context.user_data['preference']['time'] = int(time)

def update_format(mode , context:CallbackContext):
    """Updates the user's display format preference.

    Args:
        mode (str): The new format mode ('text' or 'emoji').
        context (CallbackContext): The context object containing user data.
    """
    if  "preference" not in context.user_data:
        reset_user_data(context)
    context.user_data['preference']['format'] = mode

def get_format_mode(context:CallbackContext):
    """Retrieves the user's display format preference.

    Args:
        context (CallbackContext): The context object containing user data.

    Returns:
        str: The format mode ('text' or 'emoji'). Defaults to 'text' if not found.
    """
    try:
        return context.user_data["preference"]["format"]
    except Exception:
        return 'text'

def get_user_preferences(context:CallbackContext):
    """Retrieves the user's preferred campus and time duration.

    Args:
        context (CallbackContext): The context object containing user data.

    Returns:
        tuple: A tuple (loc, time) where 'loc' is the campus identifier (or None)
               and 'time' is the duration in hours.
    """
    time = 2 # default value for quick search
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
import pytz
from datetime import datetime , timedelta
from search.find_classrooms import MAX_TIME , MIN_TIME
from typing import Tuple



def location_check(message: str , location) -> bool:
    """Verifies if the location exists in the location dictionary.

    Args:
        message (str): The location code or name to check.
        location (dict): The dictionary of valid locations.

    Returns:
        bool: True if the location is valid, False otherwise.
    """
    if message not in location:
        return False
    return True



def day_check(message:str , texts , lang) -> bool:
    """Validates the date input.

    Checks if the input matches "Today", "Tomorrow", or a valid date string (DD/MM/YYYY)
    within the next 6 days.

    Args:
        message (str): The input string to validate.
        texts (dict): Dictionary of localized texts.
        lang (str): The language code.

    Returns:
        tuple: A tuple containing (bool, str). The bool indicates validity,
               and the str is the formatted date string if valid (or the original message if not).
    """
    return_date = message
    current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
    
    # Check if message matches "Today" or "Tomorrow" in ANY language
    is_today = False
    is_tomorrow = False
    
    for l in texts:
        if message == texts[l]["keyboards"]["today"]:
            is_today = True
            break
        if message == texts[l]["keyboards"]["tomorrow"]:
            is_tomorrow = True
            break
            
    if not is_today and not is_tomorrow:
        try:
            chosen_date = datetime.strptime(message, '%d/%m/%Y').date()
            if chosen_date < current_date or chosen_date > (current_date + timedelta(days=6)):
                return False , return_date
        except ValueError:
             return False, return_date
    else:
        return_date = current_date.strftime("%d/%m/%Y") if is_today else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
        
    return True , return_date



def start_time_check(message:str) -> Tuple[bool, int]:
    """Validates the start time input.

    Args:
        message (str): The start time string (should be an integer).

    Returns:
        tuple: A tuple containing (bool, int). The bool indicates validity,
               and the int is the parsed start time. Returns (False, 0) if invalid.
    """
    start_time = 0
    try:
        start_time = int(message)
    except Exception:
        return (False,0)
    

    if start_time > MAX_TIME or start_time < MIN_TIME:
        return (False,0)
    return (True,start_time)


def end_time_check(message:str , start_time:int) -> Tuple[bool, int]:
    """Validates the end time input.

    Args:
        message (str): The end time string (should be an integer).
        start_time (int): The selected start time.

    Returns:
        tuple: A tuple containing (bool, int). The bool indicates validity,
               and the int is the parsed end time. Returns (False, 0) if invalid.
    """
    end_time = 0
    try:
        end_time = int(message)
    except Exception:
        return (False,0)    

    if int(start_time) >= end_time or end_time > MAX_TIME + 1:
        return (False,0)
    return (True,end_time)

def language_check(message ,texts):
    """Validates if the input corresponds to a supported language.

    Args:
        message (str): The language code or name to check.
        texts (dict): Dictionary of supported languages.

    Returns:
        bool: True if the language is supported, False otherwise.
    """
    if message not in texts:
        return False
    return True


def time_check(message):
    """Validates the duration input for quick search.

    Args:
        message (str): The duration input (should be an integer between 1 and 8).

    Returns:
        bool: True if the duration is valid, False otherwise.
    """
    time = 0
    try:
        time = int(message)
    except Exception as e:
        return False
    
    if time < 1 or time > 8:
        return False
    
    return True



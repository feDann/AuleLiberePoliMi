import pytz
from datetime import datetime , timedelta
from search.find_classrooms import MAX_TIME , MIN_TIME
from typing import Tuple


def location_check(message: str , location) -> bool:
    """
    Check if the location is in the location_dict
    """
    if message not in location:
        return False
    return True



def day_check(message:str , texts , lang) -> bool:
    """
    check if the input is a valid date
    """
    return_date = message
    current_date = datetime.now(pytz.timezone('Europe/Rome')).date()
    if message != texts[lang]["keyboards"]["today"] and message != texts[lang]["keyboards"]["tomorrow"]:
        chosen_date = datetime.strptime(message, '%d/%m/%Y').date()
        if chosen_date < current_date or chosen_date > (current_date + timedelta(days=6)):
            return False , return_date
    else:
        return_date = current_date.strftime("%d/%m/%Y") if message == texts[lang]["keyboards"]["today"] else (current_date + timedelta(days=1)).strftime("%d/%m/%Y")
        
    return True , return_date



def start_time_check(message:str) -> Tuple[bool, int]:
    """
    check if the start_time is an integer and if it's in the limit range
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
    """
    check in the end_time is an integer and if it's in the limit range
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
    """
    check if the input is a correct language
    """
    if message not in texts:
        return False
    return True


def time_check(message):
    """
    check if the duration for the quick search preference is a valid input
    """
    time = 0
    try:
        time = int(message)
    except Exception as e:
        return False
    
    if time < 1 or time > 8:
        return False
    
    return True



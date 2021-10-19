import pytz
from datetime import datetime , timedelta
from utils.find_classrooms import MAX_TIME , MIN_TIME
import logging

def initial_keyboard():
    return [["🔍Search" ] ,["🕒Now"] , ["ℹinfo" ,"⚙️Preferences" ]]

def search_keyboard(location_dict ):
    return [["/Cancel"]] + [[x]for x in location_dict]

def day_keyboard():
    return [["/Cancel"]] + [[(datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else ('Today' if x == 0 else 'Tomorrow')] for x in range(7)]
     
def start_time_keyboard( ):
    return [["/Cancel"]] + [[x] for x in range(MIN_TIME,MAX_TIME)]

def end_time_keyboard(start_time ):
    return [["/Cancel"]] + [[x] for x in range(start_time + 1 , MAX_TIME + 1)]

def preference_keyboard():
    return [["/Cancel"] , ["Language"] , ["Preferred Campus"] , ["Search Duration"]]

def language_keyboard(texts):
    return [["/Cancel"]] +[[lang] for lang in texts]



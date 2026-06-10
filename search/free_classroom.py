from email.policy import default
from .find_classrooms import find_classrooms
from collections import defaultdict
from pprint import pprint
from logging import root
import datetime
import json 

MAX_TIME = 20


def _is_room_free(lessons, starting_time, ending_time):
    """Checks if a room is free for the specified time interval.

    Args:
        lessons (list): A list of dictionaries representing lessons/occupancy slots.
        starting_time (float): The start time of the desired interval.
        ending_time (float): The end time of the desired interval.

    Returns:
        tuple: A tuple (is_free, until_time) where 'is_free' is a boolean and
               'until_time' is the float time until which the room is free (if applicable).
    """
    until = MAX_TIME
    
    if len(lessons) == 0:
        return (True, until)

    for lesson in lessons:
        start = float(lesson['from'])
        end = float(lesson['to'])

        if starting_time <= start and start < ending_time:
            return (False, None)

        if start <= starting_time and end > starting_time:
            return (False, None)

        if ending_time <= start and until == MAX_TIME:
            until = start

    return (True, until)


def find_free_room(starting_time , ending_time , location , day , month , year):
    """Finds available classrooms for a given time slot and location.

    Args:
        starting_time (float): The start time of the search interval.
        ending_time (float): The end time of the search interval.
        location (str): The campus location code.
        day (int): The day of the month.
        month (int): The month.
        year (int): The year.

    Returns:
        dict: A dictionary of free rooms grouped by building.
    """
    free_rooms = defaultdict(list)
    infos = find_classrooms(location , day , month , year)

    for building in infos:
        for room in infos[building]:
            lessons = infos[building][room]['lessons']
            free, until = _is_room_free(lessons , starting_time , ending_time)
            if free:
                room_info = {
                    'name' : room , 
                    'link':infos[building][room]['link'], 
                    'until': until,
                    'powerPlugs': infos[building][room]['powerPlugs']
                }
                
                free_rooms[building].append(room_info)
    
    return free_rooms


if __name__ == "__main__":
    now = datetime.datetime.now()
    info = find_free_room(9.25 , 12.25 , 'MIA', 25 , 10 , 2021)
    with open('infos_a.json' , 'w') as outfile:
        json.dump(info , outfile)
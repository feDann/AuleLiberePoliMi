from .find_classrooms import find_classrooms
from logging import root
from pprint import pprint
import datetime
import json


def _is_room_free(lessons, starting_time, ending_time):
    if len(lessons) == 0:
        return True

    for lesson in lessons:
        start = float(lesson['from'])
        end = float(lesson['to'])

        if starting_time <= start and start < ending_time:
            return False

        if start <= starting_time and end > starting_time:
            return False

    return True


def find_free_room(starting_time, ending_time, location, day, month, year):
    free_rooms = {}
    infos = find_classrooms(location, day, month, year)

    for building in infos:
        for room in infos[building]:
            lessons = infos[building][room]['lessons']

            if _is_room_free(lessons, starting_time, ending_time):
                if building not in free_rooms:
                    free_rooms[building] = []
                    
                room_info = {'name': room, 'link': infos[building][room]['link']}
                free_rooms[building].append(room_info)

    return free_rooms


if __name__ == "__main__":
    now = datetime.datetime.now()
    info = find_free_room(14.25, 18.25, 'MIA', 6, 10, 2021)

    with open('infos_a.json', 'w') as outfile:
        json.dump(info, outfile)

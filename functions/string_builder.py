from telegram.constants import MAX_MESSAGE_LENGTH


def room_builder_str(available_rooms):
    splitted_msg = []
    available_rooms_str = ""
    for building in available_rooms:
        if  MAX_MESSAGE_LENGTH - len(available_rooms_str) <= 50:
            splitted_msg.append(available_rooms_str)
            available_rooms_str = ""
        available_rooms_str += '\n<b>{}</b>\n'.format(building)
        for room in available_rooms[building]:
            available_rooms_str += ' <a href ="{}">{}</a>\n'.format(room['link'],room['name'])
    splitted_msg.append(available_rooms_str)
    return splitted_msg
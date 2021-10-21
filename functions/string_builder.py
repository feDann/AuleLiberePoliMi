from telegram.constants import MAX_MESSAGE_LENGTH


def room_builder_str(available_rooms):
    """
    this function take as input the list af all tha available classtooms
    and parse the list into a list of multiple string in order to not exceed the telegram
    len limit
    """
    splitted_msg = []
    available_rooms_str = ""
    for building in available_rooms:
        if  MAX_MESSAGE_LENGTH - len(available_rooms_str) <= 50:
            splitted_msg.append(available_rooms_str)
            available_rooms_str = ""
        available_rooms_str += '\n<b>{}</b>\n'.format(building)
        split = 0
        for room in available_rooms[building]:
            available_rooms_str += ' <a href ="{}">{}</a>  '.format(room['link'],room['name'])
            split += 1
            if split % 3 == 0:
                available_rooms_str += '\n'
    splitted_msg.append(available_rooms_str)
    return splitted_msg
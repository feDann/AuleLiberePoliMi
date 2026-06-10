from telegram.constants import MAX_MESSAGE_LENGTH
from functions import formatter


def building_builder_str(available_rooms, texts, format_mode='text'):
    """Returns a list of (building_name, formatted_string) tuples, one per building."""
    results = []
    for building in available_rooms:
        building_str = f'\n<b>{building}</b>\n'
        for room in available_rooms[building]:
            building_str += formatter.format_room(room, room['until'], format_mode, texts)
        results.append((building, building_str))
    return results


def room_builder_str(available_rooms, texts, format_mode='text'):
    """Parses the list of available classrooms and generates a list of formatted strings.

    The output is split into multiple strings if necessary to respect the Telegram
    message length limit.

    Args:
        available_rooms (dict): A dictionary where keys are building names and values are lists of room dictionaries.
        texts (dict): A dictionary of localized text strings.
        format_mode (str, optional): The display format ('text' or 'emoji'). Defaults to 'text'.

    Returns:
        list: A list of formatted strings ready to be sent as messages.
    """
    if not available_rooms:
        return []
    
    splitted_msg = []
    available_rooms_str = ""
    for building in available_rooms:
        if  MAX_MESSAGE_LENGTH - len(available_rooms_str) <= 50:
            splitted_msg.append(available_rooms_str)
            available_rooms_str = ""
        available_rooms_str += '\n<b>{}</b>\n'.format(building)
        for room in available_rooms[building]:
            available_rooms_str += formatter.format_room(room, room['until'], format_mode, texts)
    
    if available_rooms_str:
        splitted_msg.append(available_rooms_str)
        
    return splitted_msg
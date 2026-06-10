import math

def format_time(time_float):
    """Converts a floating-point time value to a string in HH:MM format.

    Args:
        time_float (float): The time to format (e.g., 15.25).

    Returns:
        str: The formatted time string (e.g., "15:15").
    """
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def format_room(room, until_time, mode, texts):
    """Formats a single room string based on the selected display mode.

    Args:
        room (dict): A dictionary containing room information (name, link, powerPlugs, etc.).
        until_time (float): The time until which the room is free.
        mode (str): The display mode, either 'text' or 'emoji'.
        texts (dict): A dictionary of localized text strings.

    Returns:
        str: The formatted string representing the room.
    """
    # Use ideographic space (U+3000) for alignment if the power plug icon is missing.
    # A normal space is too narrow compared to the emoji width.
    emoji_plug = "🔌" if room['powerPlugs'] else '\u3000'
    
    if mode == 'emoji':
        # Emoji Mode: <link>room</link> 🔌 🕒 ➜ 20:00
        formatted_time = format_time(until_time)
        return f' <a href ="{room["link"]}">{room["name"]:^10}</a> {emoji_plug} 🕒 ➜ {formatted_time}\n'
    else:
        # Text Mode (Classic): <link>room</link> (free until 20) 🔌
        # Matches the original format exactly for backward compatibility.
        emoji_plug_text = "🔌" if room['powerPlugs'] else ''
        return f' <a href ="{room["link"]}">{room["name"]:^10}</a> ({texts["until"]} {until_time}) {emoji_plug_text}\n'

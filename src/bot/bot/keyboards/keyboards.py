import os
import json
from telegram import ReplyKeyboardMarkup
from pathlib import Path
from bot.utils.locations import locations

keyboards = {
    'initial_keyboard': ['🔍Search', '🕒Now', 'ℹinfo', '⚙️Preferences'],
    'location_keyboard': ['❌Cancel'] + [location for location in  locations]
}


def get_keyboard(keyboard_name: str) -> ReplyKeyboardMarkup:
    """Build a keyboard from a list of strings

    Args:
        keyboard_name (str): name of the keyboard to build

    Returns:
        ReplyKeyboardMarkup: built keyboard
    """
    return ReplyKeyboardMarkup([keyboards[keyboard_name]], resize_keyboard=True)
from telegram import ReplyKeyboardMarkup

keyboards = {
    'initial_keyboard': ['🔍Search', '🕒Now', 'ℹinfo', '⚙️Preferences']
}


def get_keyboard(keyboard_name: str) -> ReplyKeyboardMarkup:
    """Build a keyboard from a list of strings

    Args:
        keyboard_name (str): name of the keyboard to build

    Returns:
        ReplyKeyboardMarkup: built keyboard
    """
    return ReplyKeyboardMarkup([keyboards[keyboard_name]], resize_keyboard=True)
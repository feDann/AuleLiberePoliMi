keys = {
    "search": "🔍Search",
    "now": "🕒Now",
    "info": "ℹinfo",
    "preferences": "⚙️Preferences",
    "language": "Language",
    "campus": "Preferred Campus",
    "time": "Search Duration",
    "cancel": "/Back",
    "today": "Today",
    "tomorrow": "Tomorrow",
}

def get_keys(key : str) -> str:
    """Return the button key

    Args:
        key (str): Button Key

    Returns:
        str: Button Value
    """
    return keys[key]
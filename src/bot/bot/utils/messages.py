texts = {
    "welcome": "Hi <b>{}</b>! This is Aule Libere Polimi bot, with this bot you will be able to search free classrooms for the entire week!\nThis bot is made by <b><a href='telegram.me/daniele_ferrazzo'>me</a></b>, for any issue, simply ask.\nIf you want more information select info!\nYou can terminate the conversation whenever you want using /terminate",
    "location": "Choose the location",
    "day": "Choose a day",
    "starting_time": "Choose the starting time",
    "ending_time": "Choose the ending time",
    "error": "Use the buttons you fucking donkey!",
    "ops": "In this time slot PoliMi is closed!\nI will give you instead the free classrooms of tomorrow morning from 8 a.m. to 10 a.m.",
    "terminate": "Conversation terminated!\nPress /start to start again the conversation!",
    "cancel": "Going back⬅",
    "info": 'To start the Search process simply touch the "🔍Search" button and then insert using the custom keyboard the asked information\n\nThe "🕒Now" button allows you, after setting your preferences, to quickly search the free classrooms!\n\nThe "⚙️Preferences" button allows you to set your preferences about yout preferred campus and the duration in term of hours for the quick search. Also allows you to change language! \n\nIf you want to take a look at the spaghetti code you can find it on GitHub <a href=\'https://github.com/feDann/AuleLiberePoliMi\'>here</a>',
    "settings": "This is the settings menu, from here you can choose your preferred language, preferred campus and duration time for the quick search!",
    "language": "Select your preferred language",
    "campus": "Choose the preferred campus for the quick search",
    "time": "Choose the amount of hours for the quick search",
    "success": "Done👍🏻",
    "missing": "The campus preference is missing!\nTo use this command set the campus preference",
    "exception": "An exception occurred during the search process☹️\nTry again later or contact <a href='telegram.me/daniele_ferrazzo'>me</a> for further info",
    "until": "free until",
}


def get_text(text_name: str) -> str:
    """Get a text from the texts dictionary

    Args:
        text_name (str): name of the text to get

    Returns:
        str: text
    """
    return texts[text_name]


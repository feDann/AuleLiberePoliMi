"""
This module contains the KeyboardBuilder class for creating custom Telegram keyboards.
"""
import pytz
from datetime import datetime , timedelta
from search.find_classrooms import MAX_TIME , MIN_TIME
import logging

class KeyboadBuilder:
    """Helper class to build custom ReplyKeyboards for the bot."""

    def __init__(self, texts, location_dict):
        """Initializes the KeyboardBuilder with localized texts and location data.

        Args:
            texts (dict): Dictionary of localized text strings.
            location_dict (dict): Dictionary containing campus and room data.
        """
        self.texts = texts
        self.location_dict = location_dict

    def initial_keyboard(self , lang):
        """Generates the initial main menu keyboard.

        Args:
            lang (str): The language code.

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["search"]] ,[self.texts[lang]["keyboards"]["now"]] , [self.texts[lang]["keyboards"]["info"] ,self.texts[lang]["keyboards"]["preferences"] ]]

    def location_keyboard(self, lang, campus=None):
        """Generates the location selection keyboard.

        If `campus` is None, returns the list of campuses.
        If `campus` is specified, returns the list of sub-locations (methods) for that campus,
        including a 'Back' button.

        Args:
            lang (str): The language code.
            campus (str, optional): The selected campus code. Defaults to None.

        Returns:
            list: The list of button rows for the keyboard.
        """
        cancel_label = self.texts[lang]["keyboards"]["cancel"]
        all_label = self.texts[lang]["keyboards"]["all_buildings"]

        if campus is None:
            kb = [[cancel_label]]
            for c in self.location_dict:
                kb.append([c])
            return kb

        data = self.location_dict.get(campus, {})
        sedi = data.get("sedi", {}) if isinstance(data, dict) else {}
        # First row: Cancel/Back button and 'All Buildings' search button
        kb = [[cancel_label, all_label]]
        if sedi:
            for sede in sedi:
                kb.append([sede])
        return kb

    def day_keyboard(self , lang):
        """Generates the date selection keyboard.

        Includes options for the next 7 days, with 'Today' and 'Tomorrow' localized.

        Args:
            lang (str): The language code.

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[(datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days=x)).strftime("%d/%m/%Y") if x > 1 else (self.texts[lang]["keyboards"]["today"] if x == 0 else self.texts[lang]["keyboards"]["tomorrow"])] for x in range(7)]
        
    def start_time_keyboard(self ,lang):
        """Generates the start time selection keyboard.

        Args:
            lang (str): The language code.

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(MIN_TIME,MAX_TIME)]

    def end_time_keyboard(self, lang , start_time ):
        """Generates the end time selection keyboard based on the start time.

        Args:
            lang (str): The language code.
            start_time (int): The selected start time (hour).

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(start_time + 1 , MAX_TIME + 1)]

    def preference_keyboard(self,lang):
        """Generates the settings/preferences menu keyboard.

        Args:
            lang (str): The language code.

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]] , [self.texts[lang]["keyboards"]["language"]] , [self.texts[lang]["keyboards"]["campus"]] , [self.texts[lang]["keyboards"]["time"]], [self.texts[lang]["keyboards"]["format"]]]

    def language_keyboard(self,lang):
        """Generates the language selection keyboard.

        Args:
            lang (str): The language code (unused for content, but kept for signature consistency or future use).

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]]] +[[l] for l in self.texts]

    def time_keyboard(self, lang):
        """Generates the duration selection keyboard for quick search.

        Args:
            lang (str): The language code.

        Returns:
            list: The list of button rows for the keyboard.
        """
        return [[self.texts[lang]["keyboards"]["cancel"]]] + [[x] for x in range(1 , 9)]



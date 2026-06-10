"""
This module provides the RegexBuilder class for generating regex patterns for commands.
"""
class RegexBuilder():
    """Builds regex patterns for command matching, supporting multiple aliases."""

    def __init__(self, texts):
        """Initializes the RegexBuilder.

        Args:
            texts (dict): Dictionary of localized command aliases.
        """
        self.texts = texts
        self.regex = '^({})$'


    def initial_state(self):
        """Builds the regex for the initial state commands.

        Matches 'Search', 'Now', or 'Preferences' commands in all supported languages.

        Returns:
            str: The compiled regex pattern string.
        """
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|({})|'.format(self.texts[lang]["keyboards"]["search"] , self.texts[lang]["keyboards"]["now"],self.texts[lang]["keyboards"]["preferences"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def cancel_command(self):
        """Builds the regex for the 'Cancel' command.

        Returns:
            str: The compiled regex pattern string.
        """
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|'.format(self.texts[lang]["keyboards"]["cancel"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)
    
    def date_regex(self):
        """Returns the regex pattern for validating date strings (DD/MM/YYYY or similar formats).

        Returns:
            str: The regex pattern string.
        """
        return '^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})$'
    
    def date_string_regex(self):
        """Builds the regex for 'Today' and 'Tomorrow' keywords.

        Returns:
            str: The compiled regex pattern string.
        """
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|'.format(self.texts[lang]["keyboards"]["today"] , self.texts[lang]["keyboards"]["tomorrow"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def info_regex(self):
        """Builds the regex for the 'Info' command.

        Returns:
            str: The compiled regex pattern string.
        """
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|'.format(self.texts[lang]["keyboards"]["info"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def settings_regex(self):
        """Builds the regex for the settings menu commands.

        Matches 'Campus', 'Language', 'Time', or 'Format' commands.

        Returns:
            str: The compiled regex pattern string.
        """
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|({})|({})|'.format(self.texts[lang]["keyboards"]["campus"] , self.texts[lang]["keyboards"]["language"],self.texts[lang]["keyboards"]["time"], self.texts[lang]["keyboards"]["format"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)


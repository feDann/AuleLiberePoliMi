"""
This class builds all the regex for the commands that requires multiple aliases
"""
class RegexBuilder():

    def __init__(self,texts):
        """
        take as input the texts dict
        """
        self.texts = texts
        self.regex = '^({})$'


    def initial_state(self):
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|({})|'.format(self.texts[lang]["keyboards"]["search"] , self.texts[lang]["keyboards"]["now"],self.texts[lang]["keyboards"]["preferences"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def cancel_command(self):
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|'.format(self.texts[lang]["keyboards"]["cancel"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)
    
    def date_regex(self):
        return '^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})$'
    
    def date_string_regex(self):
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|'.format(self.texts[lang]["keyboards"]["today"] , self.texts[lang]["keyboards"]["tomorrow"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def info_regex(self):
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|'.format(self.texts[lang]["keyboards"]["info"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)

    def settings_regex(self):
        or_chain = ''
        for lang in self.texts:
            or_chain += '({})|({})|({})|'.format(self.texts[lang]["keyboards"]["campus"] , self.texts[lang]["keyboards"]["language"],self.texts[lang]["keyboards"]["time"])
        or_chain = or_chain[:-1] # remove the last pipe
        return self.regex.format(or_chain)


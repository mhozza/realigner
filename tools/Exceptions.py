

class ParseException(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value
    
    def __str__(self):
        return self.value


class InvalidValueException(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        return self.value

# define the basic error class that contains its name and details about the error
class Error(Exception):
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details


# defines syntax errors
class mySyntaxError(Error):
    def __init__(self, details):
        super().__init__('Syntax Error', details)

    # defines output format
    def __str__(self):
        return f'Syntax error: {self.details} expected'


# defines illegal instances appearance
class IllegalNameError(Error):
    def __init__(self, details):
        super().__init__('Illegal Name Error', details)

    # defines output format
    def __str__(self):
        return f'IllegalNameError: Illegal name: "{self.details}" found'


# defines illegal name of identifiers
class IdentifierError(Error):
    def __init__(self, details):
        super().__init__('Illegal Name Error', details)

    # defines output format
    def __str__(self):
        return f'IdentifierError: Expected: identifier name. Found: "{self.details}"'

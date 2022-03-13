from Token import *
from Errors import *


# identifies the tokens and their types
class Lexer:
    def __init__(self, program_text):
        self.program_text = program_text  # defines source code
        self.position = 0  # defines the position of the current character in line
        self.lexer_tokens = []  # defines the set with Tokens
        self.line = ''  # defines the content from the current line
        self.delimiters = {'(', ')', '{', '}', ',', ' ', '\n', ''}
        self.operators = {'+', '-', '*', '/', '|', '&', '!', '=', '<', '>'}
        self.next_type = tuple()   # defines the type of the character next to the operator

        # analyze each line of the code
        for self.line in self.program_text:
            self.position = 0
            self.getTokensLexer()

    # finds the type of the given token; rises error in case does not much any
    def __getTokenType(self):
        token = self.line[self.position]
        # avoid invaluable characters
        if token == ' ' or token == '\n':
            self.position += 1
        # check if string
        elif token == '"':
            self.__getString()
        # checks if integers and floats
        elif '0' <= token <= '9':
            self.__getNumber()
        # checks if delimiter
        elif token in self.delimiters:
            self.__getDelimiter()
        # check if operator
        elif token in self.operators:
            self.__getOperator()
        # give a type to token
        else:
            self.__getWord()
        self.getTokensLexer()

    # get the list of tokens from lexer
    def getTokensLexer(self):
        while self.position < len(self.line):
            self.__getTokenType()

    # extracts the string type of token
    def __getString(self):
        # finds the close of the '"'
        end = self.line.find('"', self.position + 1)
        if end != -1:
            self.lexer_tokens.append(Token(STRING, self.line[self.position: end + 1]))
            self.position = end + 1
        # rise error in case of no paired '"'
        else:
            raise mySyntaxError('\'"\'')

    # itterate through a number candidate
    def __iterateNumber(self):
        while '0' <= self.line[self.position] <= '9':
            self.position += 1

    # check a token is a number
    def __getNumber(self):
        start = self.position
        check_type = True
        token_type = FLOAT
        self.__iterateNumber()
        check_type = self.checkFloat(check_type)
        # raise error in case of unacceptable characters
        if self.line[self.position] not in self.delimiters and self.line[self.position] not in self.operators:
            raise IllegalNameError(self.line[start: self.position])
        elif check_type:
            token_type = INTEGER
        # append value to the list of tokens
        self.lexer_tokens.append(Token(token_type, self.line[start: self.position]))

    # check if a number is float
    def checkFloat(self, check_type):
        if self.line[self.position] == '.':
            check_type = not check_type
            self.position += 1
            self.__iterateNumber()
        return check_type

    # check which type of delimiter
    def __getDelimiter(self):
        token = self.line[self.position]
        token_type = ""
        if token == COMMA:
            token_type = 'COMMA'
        # checks if left parenthesis
        elif token == LPARAN:
            token_type = 'LPARAN'
        # checks if right parenthesis
        elif token == RPARAN:
            token_type = 'RPARAN'
        # checks if lest brace
        elif token == LBRACE:
            token_type = 'LBRACE'
        # checks if right brace
        elif token == RBRACE:
            token_type = 'RBRACE'
        # append token to the list of tokens
        self.lexer_tokens.append(Token(token_type, token))
        # increment value
        self.position += 1

    def __getOperator(self):
        token = self.line[self.position]
        # check the folloeing character
        self.next_type = (self.position + 1, self.line[self.position + 1])
        # define the possible composed operator
        word = token + self.next_type[1]
        # check if composed operator
        if [i for i in OPERATORS if word in i]:
            token_type = ''.join([i[0] for i in OPERATORS if word in i])
            self.lexer_tokens.append(Token(token_type, word))
            self.position += 2
        #  check if one of the operators are not valid apart and raise error it yes
        elif [i for i in OPERATORS if self.next_type[1] in i] or not [i for i in OPERATORS if token in i]:
            raise mySyntaxError(f'\'{token}\'')
        # add the current valid character and increment the position
        else:
            token_type = ''.join([i[0] for i in OPERATORS if token in i])
            self.lexer_tokens.append(Token(token_type, token))
            self.position += 1

    # itterates till fit the identifier definition
    def __iterateWord(self):
        while '0' <= self.line[self.position] <= '9' or 'a' <= self.line[self.position] <= 'z' \
                or 'A' <= self.line[self.position] <= 'Z' or self.line[self.position] == '_':
            self.position += 1

    def __getWord(self):
        start = self.position  # define the start position of the word
        token = self.line[self.position]
        token_type = ""
        # check start symbol of the token
        if token != '_' and (token <= 'A' or 'Z' <= token <= 'a' or token >= 'z'):
            raise IllegalNameError(self.line[self.position])
        # iterate through word
        self.__iterateWord()
        # define the word
        word = self.line[start: self.position]
        # check if non-valid characters
        if self.line[self.position] not in self.delimiters and self.line[self.position] not in self.operators:
            IdentifierError(word)
        # check if a bool value
        elif word == 'true' or word == 'false':
            token_type = BOOL
        # check if keyword
        elif [i for i in KEYWORDS if word in i]:
            # transforms list into string
            t_type = ''.join([i[0] for i in KEYWORDS if word in i])
            # verify which character follows to avoid other defined words
            self.__checkIdentifier()
            token_type = f'KEYWORDS[{t_type}]'
        # check if in built function
        elif [i for i in IN_BUILT_FUN if word in i]:
            # transforms list into string
            t_type = ''.join([i[0] for i in IN_BUILT_FUN if word in i])
            # verify which character follows to avoid other defined words
            self.__checkIdentifier()
            token_type = f'IN_BUILT_FUN[{t_type}]'
        # assign the remained type if not any from above
        else:
            token_type = IDENTIFIER
        self.lexer_tokens.append(Token(token_type, word))

    # checks if the the following word is a keyword or in built function
    def __checkIdentifier(self):
        # get the next word
        word = self.__getNextType()
        # check if it bool
        if word == 'true' or word == 'false' or [i for i in KEYWORDS if word in i] or \
                [i for i in IN_BUILT_FUN if word in i]:
            raise IdentifierError(word)

    def __getNextType(self):
        # initiate with empty
        next_word = ""
        start = self.position
        # analyze only valid cases (keyword <' '> identifier)
        if self.line[self.position] == ' ' and self.line[self.position + 1] != '\n':
            self.position += 1
            # iterate to obtain the next word
            self.__iterateWord()
            next_word = self.line[start + 1:self.position]
            self.position = start
        return next_word

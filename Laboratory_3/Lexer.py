import re
from Token import *
from Errors import *


# identifies the tokens and their types
class Lexer:
    def __init__(self, tokenizer):
        self.tokens = tokenizer.tokenize()

    # finds the type of the given token; rises error in case does not much any
    def __getTokenType(self, token):
        # checks if string
        if token[0] == '"' and token[-1] == '"':
            return 'STRING'
        # checks if integer
        elif re.match(r'^((\+|-)?([1-9](\d*))|0)$', token):
            return INTEGER
        # checks if float
        elif re.match(r'^((\+|-)?([1-9](\d*)|0)\.(?:\d+)?)$', token):
            return FLOAT
        # checks if boolean
        elif re.match(r'(true|false)', token):
            return BOOL
        # checks if keyword
        elif [i for i in KEYWORDS if token in i]:
            token_type = ''.join([i[0] for i in KEYWORDS if token in i])  # transforms list into string
            return f'KEYWORDS[{token_type}]'
        # checks if in built function
        elif [i for i in IN_BUILT_FUN if token in i]:
            token_type = ''.join([i[0] for i in IN_BUILT_FUN if token in i])  # transforms list into string
            return f'IN_BUILT_FUN[{token_type}]'
        # checks if operator
        elif [i for i in OPERATORS if token in i]:
            return ''.join([i[0] for i in OPERATORS if token in i])
        # checks if identifier
        elif bool(re.search(r'^[A-Za-z][A-Za-z0-9_]*$', token)):
            return IDENTIFIER
        # checks if comma
        elif token == COMMA:
            return 'COMMA'
        # checks if left parenthesis
        elif token == LPARAN:
            return 'LPARAN'
        # checks if right parenthesis
        elif token == RPARAN:
            return 'RPARAN'
        # checks if lest brace
        elif token == LBRACE:
            return 'LBRACE'
        # checks if right brace
        elif token == RBRACE:
            return 'RBRACE'
        # if note any above, raises error
        else:
            raise IllegalNameError(token)

    # get the list of tokens from lexer
    def getTokensLexer(self):
        lexer_tokens = []  # list of tuples of words and their types
        # for each line
        for line_number in self.tokens:
            line = self.tokens[line_number]
            self.__buildToken(line, lexer_tokens)
        return lexer_tokens

    # builds and appends tokens to the list of tokens
    def __buildToken(self, line, lexer_tokens):
        token_count = 0
        for token in line:
            token_type = self.__getTokenType(token)
            # checks in case current word is keyword, in built function or boolean
            if token_type.find('KEYWORDS') != -1 or token_type.find('IN_BUILT_FUN') != -1 or token_type == 'BOOL':
                self.__checkIdentifier(line, token_count)
            # append to the list of tokens
            lexer_tokens.append(Token(token_type, token))
            token_count += 1

    # checks if the preceded word is a keyword or in built function
    def __checkIdentifier(self, line, index):
        if index != 0:
            # get the type of the preceded word
            pred_type = self.__getTokenType(line[index - 1])
            # raise error if the preceded word is keyword or in built function
            if pred_type.find('KEYWORDS') != -1 or pred_type.find('IN_BUILT_FUN') != -1:
                raise IdentifierError(line[index])

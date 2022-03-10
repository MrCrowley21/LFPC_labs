import re
from Errors import *


class Tokenizer:
    def __init__(self, program_text):
        self.program_text = program_text  # defines source code

    def tokenize(self):
        tokens_per_line = {}  # library that contains tokens per lines
        line_index = 0  # index of current line
        for initial_line in self.program_text:
            line_tokens = []  # tokens of the current line
            strings = r'(".*?")+'  # regex identifies strings: characters between quotes inclusively
            # add space before and after quotes
            line = re.sub(strings, r' \g<0> ', initial_line)
            # in case exists split by string
            phrases = self.__getLineStrings(line)
            self.__getTokens(phrases, line_tokens)
            if len(line_tokens) == 0:
                continue
            # add set of tokens to the dictionary and increment line index
            tokens_per_line[line_index] = line_tokens
            line_index += 1
        return tokens_per_line

    # split line by string values
    def __splitLineString(self, line):
        if '"' in line:
            return re.findall(r'[^"\s]\S*|".*?"+', line)
        else:
            return [line]

    # split line by space
    def __splitLineSpace(self, tokens):
        # adding space in the left of parenthesis if there is not any
        tokens = re.sub(r'(?<![ \\])([(){}])', r' \g<0>', tokens)
        # adding space in the right of parenthesis if there is not any
        tokens = re.sub(r'([(){}])(?! )', r'\g<0> ', tokens)
        # adding space between operators and comma and other text from the left
        tokens = re.sub(r'(?<![ \\])(,)|(?<![ &|=!><+\-*/])([&|=!><\-+*/]{1,2})', r' \g<0>', tokens)
        # adding space between operators and comma and other text from the right
        tokens = re.sub(r'(,)(?! )|([&|=!><+\-*/]{1,2})(?![ &|=!><+\-*/])', r'\g<0> ', tokens)
        # split the text by spaces
        tokens = tokens.strip().split()
        return tokens

    # checks if line may be split by strings
    def __getLineStrings(self, line):
        # checks to be pair number of '"' and splits if true
        if not (len(re.findall(r'"', line)) % 2):
            phrases = self.__splitLineString(line)
            return phrases
        # raise error otherwise
        else:
            raise mySyntaxError('\'"\'')

    # get all the remained tokens from line and append them to tokens per current line
    def __getTokens(self, phrases, line_tokens):
        for tokens in phrases:
            # in case not string
            if '"' not in tokens:
                # not analyzing empty lines
                if tokens == '' or tokens == '\n':
                    continue
                # split words by spaces and append values to the set
                tokens = self.__splitLineSpace(tokens)
                self.__appendValues(tokens, line_tokens)
            else:
                # append string to the set
                line_tokens.append(tokens)

    # append values from a list to other list
    def __appendValues(self, tokens_list, destination):
        for value in tokens_list:
            destination.append(value)

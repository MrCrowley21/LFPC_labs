from Tokenizer import *
from Lexer import *

# read the program from file and split in lines
program = open('program.txt', 'r')
lines = program.readlines()

# tokenize the program
tokenized_lines = Tokenizer(lines)
# initiate the lexer
lexer = Lexer(tokenized_lines)
# print the tokens
print(lexer.getTokensLexer())

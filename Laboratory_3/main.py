from Lexer import *

# read the program from file and split in lines
program = open('program.txt', 'r')
lines = program.readlines()

lexer = Lexer(lines)
# print the tokens
print(lexer.lexer_tokens)

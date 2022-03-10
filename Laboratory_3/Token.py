# IDENTIFIERS
IDENTIFIER = 'IDENTIFIER'

# TYPES
STRING = 'STRING'
INTEGER = 'INTEGER'
FLOAT = 'FLOAT'
BOOL = 'BOOL'

# DELIMITERS
COMMA = ','
LPARAN = '('
RPARAN = ')'
LBRACE = '{'
RBRACE = '}'

# OPERATORS
OPERATORS = [

    # ARITHMETIC
    ('PLUS', '+'),
    ('MINUS', '-'),
    ('MULTIPLICATION', '*'),
    ('DIVISION', '/'),
    ('MODULO', '//'),

    # LOGICAL
    ('AND', '&&'),
    ('OR', '||'),
    ('NOT', '!!'),

    # RELATIONAL
    ('ASSIGN', '='),
    ('EQUAL', '=='),
    ('NOT_EQUAL', '!='),
    ('GREATER', '>'),
    ('LESSER', '<'),
    ('GREATER_EQ', '>='),
    ('LESSER_EQ', '<=')
]

# KEYWORDS
KEYWORDS = [
    ('FUNCTION', 'define'),
    ('SET', 'set'),
    ('IF', 'if'),
    ('ELSE', 'else'),
    ('RETURN', 'return')
]

# IN BUILT FUNCTIONS
IN_BUILT_FUN = [
    ('PRINT', 'print')
]


# match the token and its type


class Token:
    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value

    # specifies output format of tokens
    def __repr__(self):
        if self.value:
            return f'\n{self.token_type} : {self.value}'
        return f'\n{self.token_type}'

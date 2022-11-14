from enum import Enum, auto

import ply.lex as lex


reserved_words = {
   'IF': 'IF',
   'THEN': 'THEN',
   'ELSE': 'ELSE',
   'END': 'END',
   'WHILE': 'WHILE',
   'NOT': 'NOT',
   'TO': 'TO',
   'AND': 'AND',
   'OR': 'OR',
   'SET': 'SET',
}


class TokenType(Enum):
    NUMBER = auto()
    POW = "^"
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    DIVIDE = "/"
    LPAREN = "("
    RPAREN = ")"
    EQUAL = "="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    IS_EQUAL = "=="
    NOT_EQUAL = "<>"
    COLON = ":"
    ID = auto()
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    END = "END"
    WHILE = "WHILE"
    NOT = "NOT"
    TO = "TO"
    AND = "AND"
    OR = "OR"
    SET = "SET"


def enum_names(enum):
    return list(map(lambda e: e.name, enum))


# List of token names.   This is always required
tokens = enum_names(TokenType)

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_POW = r'\^'

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_EQUAL = '='

t_COLON = r':'

t_GREATER_THAN = r'>'
t_GREATER_EQUAL = r'>='
t_LESS_THAN = r'<'
t_LESS_EQUAL = r'<='
t_IS_EQUAL = r'=='
t_NOT_EQUAL = r'<>'


# A regular expression rule with some action code
def t_NUMBER(t):
    r'(-)?[0-9]+(\.[0-9]+)?'
    t.value = float(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_words.get(t.value.upper(), 'ID')
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


if __name__ == '__main__':
    # Build the lexer

    # Test it out
    data = '''
     IF X > 2 THEN FUNC END
     '''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)
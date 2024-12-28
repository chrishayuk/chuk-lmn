# lmn/compiler/lexer/token_type.py
from enum import Enum

class LmnTokenType(Enum):
    # ------------------------------
    # Basic Value/Identifier Tokens
    # ------------------------------
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'
    NEWLINE = 'NEWLINE'  # Use if needed; else remove

    # ------------------------------
    # Numeric (literals)
    # ------------------------------
    INT_LITERAL      = 'INT_LITERAL'      # 32-bit integer literal
    LONG_LITERAL     = 'LONG_LITERAL'     # 64-bit integer literal
    FLOAT_LITERAL    = 'FLOAT_LITERAL'    # float literal (f suffix)
    DOUBLE_LITERAL   = 'DOUBLE_LITERAL'   # double literal (no f suffix)

    # ------------------------------
    # Operators
    # ------------------------------
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    POW = '^'

    # ------------------------------
    # Punctuation
    # ------------------------------
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    LBRACKET = '['
    RBRACKET = ']'
    DOT = 'DOT'
    COLON = ':'

    # ------------------------------
    # Comment
    # ------------------------------
    COMMENT = 'COMMENT'

    # ------------------------------
    # Keywords (all lowercase)
    # ------------------------------
    FUNCTION = 'function'
    LET = 'let'
    PRINT = 'print'
    IF = 'if'
    ELSE = 'else'
    END = 'end'
    RETURN = 'return'
    CALL = 'call'
    FOR = 'for'
    TO = 'to'
    IN = 'in'
    AND = 'and'
    OR = 'or'
    NOT = 'not'
    BREAK = 'break'
    TRUE = 'true'
    FALSE = 'false'
    NIL = 'nil'

    # ------------------------------
    # Type Keywords
    # ------------------------------
    INT    = 'int'
    LONG   = 'long'
    FLOAT  = 'float'
    DOUBLE = 'double'

    @staticmethod
    def get_keywords():
        """
        Maps lowercase keyword strings to the corresponding enum member.
        """
        return {
            'function': LmnTokenType.FUNCTION,
            'let': LmnTokenType.LET,
            'print': LmnTokenType.PRINT,
            'if': LmnTokenType.IF,
            'else': LmnTokenType.ELSE,
            'end': LmnTokenType.END,
            'return': LmnTokenType.RETURN,
            'call': LmnTokenType.CALL,
            'for': LmnTokenType.FOR,
            'to': LmnTokenType.TO,
            'in': LmnTokenType.IN,
            'and': LmnTokenType.AND,
            'or': LmnTokenType.OR,
            'not': LmnTokenType.NOT,
            'break': LmnTokenType.BREAK,
            'true': LmnTokenType.TRUE,
            'false': LmnTokenType.FALSE,
            'nil': LmnTokenType.NIL,

            # Type keywords
            'int': LmnTokenType.INT,
            'long': LmnTokenType.LONG,
            'float': LmnTokenType.FLOAT,
            'double': LmnTokenType.DOUBLE,
        }

    @staticmethod
    def get_operator_map():
        return {
            '!=': LmnTokenType.NE,
            '<=': LmnTokenType.LE,
            '>=': LmnTokenType.GE,
            '<':  LmnTokenType.LT,
            '>':  LmnTokenType.GT,
            '=':  LmnTokenType.EQ,
            '+':  LmnTokenType.PLUS,
            '-':  LmnTokenType.MINUS,
            '*':  LmnTokenType.MUL,
            '/':  LmnTokenType.DIV,
            '^':  LmnTokenType.POW
        }

    @staticmethod
    def get_punctuation_map():
        return {
            '(': LmnTokenType.LPAREN,
            ')': LmnTokenType.RPAREN,
            ',': LmnTokenType.COMMA,
            '[': LmnTokenType.LBRACKET,
            ']': LmnTokenType.RBRACKET,
            '.': LmnTokenType.DOT,
            ':': LmnTokenType.COLON,
        }

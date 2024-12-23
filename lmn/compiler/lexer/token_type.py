from enum import Enum

class LmnTokenType(Enum):
    # ------------------------------
    # Basic Value/Identifier Tokens
    # ------------------------------
    STRING = 'STRING'         # e.g., "hello"
    NUMBER = 'NUMBER'         # e.g., 123, 3.14
    IDENTIFIER = 'IDENTIFIER' # e.g., myVar, fact, city
    NEWLINE = 'NEWLINE'       # representing a line break

    # ------------------------------
    # Operators
    # ------------------------------
    EQ = '='       # can be used for equality (expr-level) or assignment (depending on grammar)
    NE = '!='      # not-equal
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    POW = '^'      # optional exponent operator

    # ------------------------------
    # Punctuation
    # ------------------------------
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    LBRACKET = '['
    RBRACKET = ']'

    # ------------------------------
    # Comment
    # ------------------------------
    COMMENT = 'COMMENT'       # e.g., everything after "//" until end of line

    # ------------------------------
    # Keywords (all lowercase)
    # ------------------------------
    FUNCTION = 'function'
    SET = 'set'
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

    @staticmethod
    def get_keywords():
        """
        Maps lowercase keyword strings to the corresponding enum member.
        """
        return {
            'function': LmnTokenType.FUNCTION,
            'set': LmnTokenType.SET,
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
            'nil': LmnTokenType.NIL
        }

    @staticmethod
    def get_operator_map():
        return {
            # Multi-char first
            '!=': LmnTokenType.NE,
            '<=': LmnTokenType.LE,
            '>=': LmnTokenType.GE,
            # Then single-char
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
        """
        Maps punctuation characters to the corresponding enum member.
        """
        return {
            '(': LmnTokenType.LPAREN,
            ')': LmnTokenType.RPAREN,
            ',': LmnTokenType.COMMA,
            '[': LmnTokenType.LBRACKET,
            ']': LmnTokenType.RBRACKET
        }

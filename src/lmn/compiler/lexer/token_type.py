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
    EQEQ  = '=='
    NE = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'

    # Extended operators
    MOD         = '%'      # modulo operator
    FLOORDIV    = '//'     # integer division
    INC         = '++'     # postfix increment
    DEC         = '--'     # postfix decrement
    PLUS_EQ     = '+='     # compound assignment (a += x)
    MINUS_EQ    = '-='     # compound assignment (a -= x)
    EQ_PLUS     = '=+'     # alternative compound assignment (a =+ x)
    EQ_MINUS    = '=-'     # alternative compound assignment (a =- x)

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

    # Scope
    BEGIN = 'begin'
    END = 'end'

    # Functions
    FUNCTION = 'function'
    RETURN = 'return'

    # Control
    IF = 'if'
    ELSE = 'else'
    ELSEIF = 'elseif'

    # Loops
    FOR = 'for'
    TO = 'to'
    IN = 'in'
    BREAK = 'break'
    CONTINUE = 'continue'

    # Statements
    LET = 'let'
    PRINT = 'print'
    CALL = 'call'
    AND = 'and'
    OR = 'or'
    NOT = 'not'
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
            # scope
            'begin': LmnTokenType.BEGIN,
            'end': LmnTokenType.END,

            # functions
            'function': LmnTokenType.FUNCTION,
            'return': LmnTokenType.RETURN,

            # control
            'if': LmnTokenType.IF,
            'else': LmnTokenType.ELSE,
            'elseif': LmnTokenType.ELSEIF,

            # loops
            'for': LmnTokenType.FOR,
            'to': LmnTokenType.TO,
            'in': LmnTokenType.IN,
            'break': LmnTokenType.BREAK,

            # statements
            'let': LmnTokenType.LET,
            'print': LmnTokenType.PRINT,
            'call': LmnTokenType.CALL,
            'and': LmnTokenType.AND,
            'or': LmnTokenType.OR,
            'not': LmnTokenType.NOT,
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
            '==': LmnTokenType.EQEQ,
            '!=': LmnTokenType.NE,
            '<=': LmnTokenType.LE,
            '>=': LmnTokenType.GE,
            '<':  LmnTokenType.LT,
            '>':  LmnTokenType.GT,
            # Multi-character operators first, so they don't get overshadowed:
            '//': LmnTokenType.FLOORDIV,
            '++': LmnTokenType.INC,
            '--': LmnTokenType.DEC,
            '+=': LmnTokenType.PLUS_EQ,
            '-=': LmnTokenType.MINUS_EQ,
            '=+': LmnTokenType.EQ_PLUS,
            '=-': LmnTokenType.EQ_MINUS,
            # Single-character operators
            '=':  LmnTokenType.EQ,
            '+':  LmnTokenType.PLUS,
            '-':  LmnTokenType.MINUS,
            '*':  LmnTokenType.MUL,
            '/':  LmnTokenType.DIV,
            '%':  LmnTokenType.MOD
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

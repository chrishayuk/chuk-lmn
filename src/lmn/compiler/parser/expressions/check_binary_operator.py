# file: lmn/compiler/parser/expressions/check_binary_operator.py
from lmn.compiler.lexer.token_type import LmnTokenType

def _is_binary_operator(self, token):
    if not token:
        return False
    
    return token.token_type in [
        # Basic arithmetic
        LmnTokenType.PLUS,
        LmnTokenType.MINUS,
        LmnTokenType.MUL,
        LmnTokenType.DIV,

        # Extended arithmetic
        LmnTokenType.FLOORDIV,
        LmnTokenType.MOD,

        # Comparisons
        LmnTokenType.EQEQ,
        LmnTokenType.NE,
        LmnTokenType.LT,
        LmnTokenType.LE,
        LmnTokenType.GT,
        LmnTokenType.GE,

        # Logical
        LmnTokenType.AND,
        LmnTokenType.OR,

        # # Bitwise (example additions, if your language supports them)
        # LmnTokenType.BITAND,    # e.g. '&'
        # LmnTokenType.BITOR,     # e.g. '|'
        # LmnTokenType.SHL,       # e.g. '<<'
        # LmnTokenType.SHR,       # e.g. '>>'
    ]

# lmn/compiler/parser/statements/statement_boundaries.py
from lmn.compiler.lexer.token_type import LmnTokenType

STATEMENT_BOUNDARY_TOKENS = {
    LmnTokenType.IF,
    LmnTokenType.FOR,
    LmnTokenType.LET,
    LmnTokenType.PRINT,
    LmnTokenType.RETURN,
    LmnTokenType.END,
    LmnTokenType.ELSE,
    LmnTokenType.FUNCTION,
    LmnTokenType.CALL,
    LmnTokenType.BEGIN,
}

def is_statement_boundary(token_type):
    """
    Returns True if the token type indicates the start of a new statement
    or a block boundary.
    """
    return token_type in STATEMENT_BOUNDARY_TOKENS
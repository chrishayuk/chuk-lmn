# file: lmn/compiler/parser/statements/statement_boundaries.py
from lmn.compiler.lexer.token_type import LmnTokenType

# The original boundary set for top-level statements
STATEMENT_BOUNDARY_TOKENS = {
    LmnTokenType.IF,
    LmnTokenType.ELSEIF,
    LmnTokenType.FOR,
    LmnTokenType.LET,
    LmnTokenType.PRINT,
    LmnTokenType.RETURN,
    LmnTokenType.END,
    LmnTokenType.ELSE,
    LmnTokenType.FUNCTION,  # We'll exclude this only when in expression context
    LmnTokenType.CALL,
    LmnTokenType.BEGIN,
}

def is_statement_boundary(token_type, in_expression: bool = False) -> bool:
    """
    If in_expression=True, we treat 'function' as *not* a statement boundary
    so inline function expressions parse correctly.
    If in_expression=False, 'function' is a boundary for top-level function defs.
    """
    if token_type is None:
        return True

    if in_expression:
        # Exclude FUNCTION from the boundary so inline function can parse
        boundary_tokens = STATEMENT_BOUNDARY_TOKENS - {LmnTokenType.FUNCTION}
    else:
        boundary_tokens = STATEMENT_BOUNDARY_TOKENS

    return token_type in boundary_tokens

# lmn/compiler/parser/expressions/statement_boundaries.py
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
}

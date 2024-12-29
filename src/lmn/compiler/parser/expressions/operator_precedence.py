# file: lmn/compiler/parser/expressions/operator_precedence.py
from lmn.compiler.lexer.token_type import LmnTokenType

OP_PRECEDENCE = {
    # Multiplicative
    LmnTokenType.MUL: 3,
    LmnTokenType.DIV: 3,
    LmnTokenType.FLOORDIV: 3,
    LmnTokenType.MOD: 3,

    # Additive
    LmnTokenType.PLUS: 2,
    LmnTokenType.MINUS: 2,

    # Comparisons
    LmnTokenType.LT: 1,
    LmnTokenType.LE: 1,
    LmnTokenType.GT: 1,
    LmnTokenType.GE: 1,
    LmnTokenType.EQEQ: 1,
    LmnTokenType.NE: 1,

    # Logical
    LmnTokenType.AND: 0,
    LmnTokenType.OR:  0,
}

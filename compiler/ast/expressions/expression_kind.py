# compiler/ast/expressions/expression_kind.py
from enum import Enum

class ExpressionKind(str, Enum):
    """
    Enumerates the 'type' strings used by Expression classes.
    This helps avoid repeated string literals & ensures we
    only allow valid kinds.
    """
    EXPRESSION = "Expression"
    BINARY = "BinaryExpression"
    UNARY = "UnaryExpression"
    LITERAL = "LiteralExpression"
    VARIABLE = "VariableExpression"
    FN = "FnExpression"
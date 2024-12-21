# compiler/ast/expressions/variable_expression.py
from typing import Literal
from compiler.ast.expressions.expression import Expression
from compiler.ast.expressions.expression_kind import ExpressionKind

class VariableExpression(Expression):
    """
    A variable reference, e.g. x or fact
    """
    type: Literal[ExpressionKind.VARIABLE] = ExpressionKind.VARIABLE
    name: str

    def __str__(self):
        return self.name

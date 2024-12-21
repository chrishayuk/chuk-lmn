# compiler/ast/expressions/binary_expression.py
from typing import Literal
from compiler.ast.expressions.expression import Expression
from compiler.ast.expressions.expression_kind import ExpressionKind
from compiler.ast.expressions.expression_union import ExpressionUnion

class BinaryExpression(Expression):
    type: Literal[ExpressionKind.BINARY] = ExpressionKind.BINARY
    operator: str
    left: ExpressionUnion
    right: ExpressionUnion

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

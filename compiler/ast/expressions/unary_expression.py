# compiler/ast/expressions/unary_expression.py
from typing import Literal
from compiler.ast.expressions.expression import Expression
from compiler.ast.expressions.expression_kind import ExpressionKind
from compiler.ast.expressions.expression_union import ExpressionUnion

class UnaryExpression(Expression):
    type: Literal[ExpressionKind.UNARY] = ExpressionKind.UNARY
    operator: str
    operand: ExpressionUnion

    def __str__(self):
        return f"({self.operator} {self.operand})"

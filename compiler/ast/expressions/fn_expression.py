# compiler/ast/expressions/fn_expression.py
from typing import List, Literal
from pydantic import Field
from compiler.ast.expressions.expression import Expression
from compiler.ast.expressions.expression_kind import ExpressionKind
from compiler.ast.expressions.expression_union import ExpressionUnion

class FnExpression(Expression):
    type: Literal[ExpressionKind.FN] = ExpressionKind.FN
    name: ExpressionUnion
    arguments: List[ExpressionUnion] = Field(default_factory=list)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"

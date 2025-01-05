# file: lmn/compiler/ast/expressions/unary_expression.py
from __future__ import annotations
from typing import Literal, Optional

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class UnaryExpression(ExpressionBase):
    """
    A unary expression node, e.g. -(operand) or not(operand).
    Inherits from ExpressionBase for shared fields like inferred_type.
    """
    # set the node as Unary
    type: Literal["UnaryExpression"] = "UnaryExpression"
    

    # operator
    operator: str
    operand: "Expression"

    # inferred type
    inferred_type: Optional[str] = None

    def __str__(self):
        return f"({self.operator} {self.operand})"

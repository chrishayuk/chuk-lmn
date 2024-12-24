# file: lmn/compiler/ast/expressions/unary_expression.py
from __future__ import annotations
from typing import Literal, Optional

# import ast's
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class UnaryExpression(ExpressionBase):
    """
    A unary expression node, e.g. -(operand) or not(operand).
    Inherits from ExpressionBase for shared fields like inferred_type.
    """
    type: Literal[NodeKind.UNARY] = NodeKind.UNARY
    operator: str
    operand: "Expression"

    inferred_type: Optional[str] = None

    def __str__(self):
        return f"({self.operator} {self.operand})"

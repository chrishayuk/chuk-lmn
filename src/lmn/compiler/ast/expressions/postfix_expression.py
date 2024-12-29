# file: lmn/compiler/ast/expressions/postfix_expression.py
from __future__ import annotations
from typing import Literal, Optional

from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class PostfixExpression(ExpressionBase):
    """
    A postfix expression node, e.g. operand++ or operand--.
    Inherits from ExpressionBase for shared fields like inferred_type.
    """
    type: Literal[NodeKind.POSTFIX] = NodeKind.POSTFIX
    operator: str
    operand: "Expression"  # The sub-expression being incremented/decremented
    inferred_type: Optional[str] = None

    def __str__(self):
        # For printing/debugging, e.g. '(x++)'
        return f"({self.operand}{self.operator})"

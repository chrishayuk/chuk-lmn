# file: lmn/compiler/ast/expressions/postfix_expression.py
from __future__ import annotations
from typing import Literal, Optional

# lmn imports
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class PostfixExpression(ExpressionBase):
    """
    A postfix expression node, e.g. operand++ or operand--.
    Inherits from ExpressionBase for shared fields like inferred_type.
    """
    # set the type as postfix
    type: Literal["PostfixExpression"] = "PostfixExpression"

    # set the operator
    operator: str
    operand: "Expression"  # The sub-expression being incremented/decremented

    def __str__(self):
        # For printing/debugging, e.g. '(x++)'
        return f"({self.operand}{self.operator})"

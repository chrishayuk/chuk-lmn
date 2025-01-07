# file: lmn/compiler/ast/expressions/binary_expression.py
from __future__ import annotations
from typing import Literal, Optional

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class BinaryExpression(ExpressionBase):
    """ A binary expression node, e.g. (a + b). """
    # binary expression node, e.g. (a + b)
    type: Literal["BinaryExpression"] = "BinaryExpression"

    # The operator, e.g. '+'
    operator: str

    # We reference the 'Expression' union as a **string** (forward ref),
    # so we do NOT import mega_union here. That avoids circular import.

    # left and right are expressions
    left: "Expression"  
    right: "Expression"

    def __str__(self):
        # Return the string representation of the binary expression
        return f"({self.left} {self.operator} {self.right})"

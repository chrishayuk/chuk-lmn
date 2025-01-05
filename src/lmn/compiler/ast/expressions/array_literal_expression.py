# file: lmn/compiler/ast/expressions/array_literal_expression.py
from __future__ import annotations
from typing import List, Literal

# lmn imports
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class ArrayLiteralExpression(ExpressionBase):
    """
    Example node for array literals in the AST.
    Each 'element' is a normal Expression, so we can have anything inside.
    """
    # type of the node is ARRAY_LITERAL
    type: Literal["ArrayLiteralExpression"] = "ArrayLiteralExpression"

    # list of elements inside the array as expressions
    elements: List["Expression"]  

    def __str__(self):
        # return a string representation of the node
        return f"[{', '.join(str(e) for e in self.elements)}]"

# file: lmn/compiler/ast/expressions/variable_expression.py
from __future__ import annotations
from typing import Literal, Optional

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class VariableExpression(ExpressionBase):
    """
    A variable reference, e.g. x or fact
    """
    # node type is VARIABLE
    type: Literal["VariableExpression"] = "VariableExpression"

    # name of the variable
    name: str

    def __str__(self):
        return self.name

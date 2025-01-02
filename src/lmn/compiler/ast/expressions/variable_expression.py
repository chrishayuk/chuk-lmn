# file: lmn/compiler/ast/expressions/variable_expression.py
from __future__ import annotations
from typing import Literal, Optional

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

class VariableExpression(ExpressionBase):
    """
    A variable reference, e.g. x or fact
    """
    # node type is VARIABLE
    type: Literal[NodeKind.VARIABLE] = NodeKind.VARIABLE

    # name of the variable
    name: str

    # inferred type of the variable
    inferred_type: Optional[str] = None

    def __str__(self):
        return self.name

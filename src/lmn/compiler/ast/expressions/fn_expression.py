# file: lmn/compiler/ast/expressions/fn_expression.py
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import Field

# Import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

class FnExpression(ExpressionBase):
    """
    A function expression node, e.g. name(args...).
    'name' can be another expression (like a variable) or a literal,
    and 'arguments' are expressions as well.
    """

    # set the node kind as a function expression
    type: Literal[NodeKind.FN] = NodeKind.FN

    # We use forward references ("Expression") to avoid circular imports.

    # name of the function expression
    name: "Expression"

    # arguments of the function expression
    arguments: List["Expression"] = Field(default_factory=list)

    # inferred type of the function expression
    inferred_type: Optional[str] = None

    def __str__(self):
        # output the node as a string
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"

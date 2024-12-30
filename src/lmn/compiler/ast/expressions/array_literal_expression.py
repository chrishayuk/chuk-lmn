# file: lmn/compiler/ast/expressions/array_literal_expression.py
from __future__ import annotations
from typing import List, Literal
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

class ArrayLiteralExpression(ExpressionBase):
    """
    Example node for array literals in the AST.
    Each 'element' is a normal Expression, so we can have anything inside.
    """
    type: Literal[NodeKind.ARRAY_LITERAL] = NodeKind.ARRAY_LITERAL
    elements: List["Expression"]  # 'Expression' is your union of expressions

    def __str__(self):
        return f"[{', '.join(str(e) for e in self.elements)}]"

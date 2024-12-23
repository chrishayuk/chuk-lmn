# lmn/compiler/ast/expressions/variable_expression.py
from __future__ import annotations
from typing import Literal

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class VariableExpression(ASTNode):
    """
    A variable reference, e.g. x or fact
    """
    type: Literal[NodeKind.VARIABLE] = NodeKind.VARIABLE
    name: str

    def __str__(self):
        return self.name

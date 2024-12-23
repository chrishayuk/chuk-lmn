# lmn/compiler/ast/expressions/binary_expression.py
from __future__ import annotations
from typing import Literal

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.mega_union import MegaUnion

class BinaryExpression(ASTNode):
    type: Literal[NodeKind.BINARY] = NodeKind.BINARY
    operator: str
    left: MegaUnion
    right: MegaUnion

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

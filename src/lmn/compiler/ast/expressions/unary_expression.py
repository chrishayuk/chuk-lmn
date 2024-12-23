# lmn/compiler/ast/expressions/unary_expression.py
from __future__ import annotations
from typing import Literal

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.mega_union import MegaUnion

class UnaryExpression(ASTNode):
    type: Literal[NodeKind.UNARY] = NodeKind.UNARY
    operator: str
    operand: MegaUnion

    def __str__(self):
        return f"({self.operator} {self.operand})"

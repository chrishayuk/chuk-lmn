# compiler/ast/expressions/unary_expression.py
from __future__ import annotations
from typing import Literal

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class UnaryExpression(ASTNode):
    type: Literal[NodeKind.UNARY] = NodeKind.UNARY
    operator: str
    operand: MegaUnion

    def __str__(self):
        return f"({self.operator} {self.operand})"

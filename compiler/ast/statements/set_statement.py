# compiler/ast/statements/set_statement.py
from __future__ import annotations
from typing import Literal

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class SetStatement(ASTNode):
    type: Literal[NodeKind.SET] = NodeKind.SET
    variable: MegaUnion
    expression: MegaUnion

    def __str__(self):
        return f"set {self.variable} = {self.expression}"

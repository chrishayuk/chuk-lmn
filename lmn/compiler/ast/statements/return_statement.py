# compiler/ast/statements/return_statement.py
from __future__ import annotations
from typing import Optional, Literal
from pydantic import Field

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class ReturnStatement(ASTNode):
    type: Literal[NodeKind.RETURN] = NodeKind.RETURN
    expression: Optional[MegaUnion] = None

    def __str__(self):
        return f"return {self.expression}"

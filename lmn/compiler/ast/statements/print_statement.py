# compiler/ast/statements/print_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class PrintStatement(ASTNode):
    type: Literal[NodeKind.PRINT] = NodeKind.PRINT
    expressions: List[MegaUnion] = Field(default_factory=list)

    def __str__(self):
        return "print " + " ".join(str(expr) for expr in self.expressions)

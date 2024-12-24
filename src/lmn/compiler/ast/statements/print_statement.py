# file: lmn/compiler/ast/statements/print_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class PrintStatement(ASTNode):
    """
    A 'print' statement that prints one or more expressions/nodes.
    e.g. print expr1 expr2 ...
    """
    type: Literal[NodeKind.PRINT] = NodeKind.PRINT
    expressions: List["Expression"] = Field(default_factory=list)

    def __str__(self):
        return "print " + " ".join(str(expr) for expr in self.expressions)

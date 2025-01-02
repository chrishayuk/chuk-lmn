# file: lmn/compiler/ast/statements/print_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class PrintStatement(ASTNode):
    """
    A 'print' statement that prints one or more expressions/nodes.
    e.g. print expr1 expr2 ...
    """
    # set the type of this node to be 'PRINT'
    type: Literal[NodeKind.PRINT] = NodeKind.PRINT

    # a list of expressions/nodes to be printed
    expressions: List["Expression"] = Field(default_factory=list)

    def __str__(self):
        # output the node as a string
        return "print " + " ".join(str(expr) for expr in self.expressions)

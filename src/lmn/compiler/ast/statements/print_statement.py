# file: lmn/compiler/ast/statements/print_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class PrintStatement(StatementBase):
    """
    A 'print' statement that prints one or more expressions/nodes.
    e.g. print expr1 expr2 ...
    """
    # set the type of this node to be 'PRINT'
    type: Literal["PrintStatement"] = "PrintStatement"
    

    # a list of expressions/nodes to be printed
    expressions: List["Expression"] = Field(default_factory=list)

    def __str__(self):
        # output the node as a string
        return "print " + " ".join(str(expr) for expr in self.expressions)

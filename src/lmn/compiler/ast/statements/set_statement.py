# file: lmn/compiler/ast/statements/set_statement.py
from __future__ import annotations
from typing import Literal

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class SetStatement(ASTNode):
    """
    Represents a 'set' statement, e.g.:
      set <variable> = <expression>
    """
    type: Literal[NodeKind.SET] = NodeKind.SET
    variable: "Expression"
    expression: "Expression"

    def __str__(self):
        return f"set {self.variable} = {self.expression}"

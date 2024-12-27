# file: lmn/compiler/ast/statements/let_statement.py
from __future__ import annotations
from typing import Literal, Optional
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class LetStatement(ASTNode):
    """
    Represents a 'set' statement, e.g.:
      let <variable> = <expression>
    But we also allow no initializer: set x
    """
    type: Literal[NodeKind.LET] = NodeKind.LET
    variable: "Expression"

    # optional expression
    expression: Optional["Expression"] = None

    def __str__(self):
        # If expression is None, just print 'set variable'
        if self.expression is None:
            return f"let {self.variable}"
        return f"let {self.variable} = {self.expression}"

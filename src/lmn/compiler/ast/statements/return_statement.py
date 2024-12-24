# file: lmn/compiler/ast/statements/return_statement.py
from __future__ import annotations
from typing import Optional, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class ReturnStatement(ASTNode):
    """
    Represents a 'return' statement, optionally returning an expression.
    e.g. return expr
    """
    type: Literal[NodeKind.RETURN] = NodeKind.RETURN

    # If there's an expression to return, we reference 'Node' by a string
    # to avoid importing the union directly.
    expression: Optional["Expression"] = None

    def __str__(self):
        return f"return {self.expression}"

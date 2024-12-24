# file: lmn/compiler/ast/statements/call_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# ast nodes
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class CallStatement(ASTNode):
    """
    Represents: call "someTool" expr1 expr2 ...
    """
    type: Literal[NodeKind.CALL] = NodeKind.CALL
    tool_name: str

    # arguments
    arguments: List["Expression"] = Field(default_factory=list)

    def __str__(self):
        args_str = " ".join(str(arg) for arg in self.arguments)
        return f'call "{self.tool_name}" {args_str}'

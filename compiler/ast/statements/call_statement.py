# compiler/ast/statements/call_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class CallStatement(ASTNode):
    """
    Represents: call "someTool" expr1 expr2 ...
    """
    type: Literal[NodeKind.CALL] = NodeKind.CALL
    tool_name: str
    # arguments can hold expressions or other nodes => MegaUnion
    arguments: List[MegaUnion] = Field(default_factory=list)

    def __str__(self):
        args_str = " ".join(str(arg) for arg in self.arguments)
        return f'call "{self.tool_name}" {args_str}'

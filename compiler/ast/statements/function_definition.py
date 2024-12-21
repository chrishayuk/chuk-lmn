# compiler/ast/statements/function_definition.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class FunctionDefinition(ASTNode):
    type: Literal[NodeKind.FUNCTION_DEF] = NodeKind.FUNCTION_DEF
    name: str
    parameters: List[str] = Field(default_factory=list)
    # The body holds sub-statements => MegaUnion
    body: List[MegaUnion] = Field(default_factory=list)

    def __str__(self):
        params_str = ", ".join(self.parameters)
        body_str = " ".join(str(stmt) for stmt in self.body)
        return f"function {self.name}({params_str}) [body: {body_str}]"

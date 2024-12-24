# file: lmn/compiler/ast/statements/function_definition.py

from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class FunctionDefinition(ASTNode):
    """
    Represents a function definition, e.g.:
      function myFunc(param1, param2) { ...body statements... }
    """
    type: Literal[NodeKind.FUNCTION_DEF] = NodeKind.FUNCTION_DEF

    name: str
    params: List[str] = Field(default_factory=list)

    # we use a string-based forward reference:
    body: List["Node"] = Field(default_factory=list)

    def __str__(self):
        params_str = ", ".join(self.params)
        body_str = " ".join(str(stmt) for stmt in self.body)
        return f"function {self.name}({params_str}) [body: {body_str}]"

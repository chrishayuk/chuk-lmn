# lmn/compiler/ast/statements/function_definition.py

from typing import List, Literal
from pydantic import Field
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.statements.function_parameter import FunctionParameter
# or if you put it in a different location, import from that file

class FunctionDefinition(ASTNode):
    type: Literal[NodeKind.FUNCTION_DEF] = NodeKind.FUNCTION_DEF

    name: str
    # Now 'params' is a list of FunctionParameter nodes
    params: List[FunctionParameter] = Field(default_factory=list)
    body: List["Node"] = Field(default_factory=list)

    def __str__(self):
        params_str = ", ".join(
            p.name + (f":{p.type_annotation}" if p.type_annotation else "")
            for p in self.params
        )
        body_str = " ".join(str(stmt) for stmt in self.body)
        return f"function {self.name}({params_str}) [body: {body_str}]"

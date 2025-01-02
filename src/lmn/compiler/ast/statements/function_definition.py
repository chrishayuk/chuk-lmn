# lmn/compiler/ast/statements/function_definition.py
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.statements.function_parameter import FunctionParameter

class FunctionDefinition(ASTNode):
    # The kind of the node
    type: Literal[NodeKind.FUNCTION_DEF] = NodeKind.FUNCTION_DEF

    # name of the function
    name: str

    # Now 'params' is a list of FunctionParameter nodes
    params: List[FunctionParameter] = Field(default_factory=list)

    # Now 'body' is a list of Node objects
    body: List["Node"] = Field(default_factory=list)

    def __str__(self):
        # create a string representation of the parameters
        params_str = ", ".join(
            p.name + (f":{p.type_annotation}" if p.type_annotation else "")
            for p in self.params
        )

        # set the body to be a list of statements
        body_str = " ".join(str(stmt) for stmt in self.body)

        # return the string representation of the object
        return f"function {self.name}({params_str}) [body: {body_str}]"

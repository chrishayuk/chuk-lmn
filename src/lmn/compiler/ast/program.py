# file: lmn/compiler/ast/program.py
from typing import List, Literal
from pydantic import Field

# ast's
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class Program(ASTNode):
    # program node type
    type: Literal["Program"] = "Program"

    # Use a string-based forward reference for 'Node':
    # so we do not import the union directly (which can cause circular imports).

    # list of nodes for the program
    body: List["Node"] = Field(default_factory=list)

    def add_statement(self, stmt: "Node") -> None:
        # add statement to the program
        self.body.append(stmt)

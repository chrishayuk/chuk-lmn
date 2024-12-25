# file: lmn/compiler/ast/program.py
from typing import List, Literal
from pydantic import Field

# ast's
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class Program(ASTNode):
    type: Literal["Program"] = "Program"

    # Use a string-based forward reference for 'Node':
    # so we do not import the union directly (which can cause circular imports).
    body: List["Node"] = Field(default_factory=list)

    def add_statement(self, stmt: "Node") -> None:
        self.body.append(stmt)

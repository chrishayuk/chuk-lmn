# file: lmn/compiler/ast/statements/block_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class BlockStatement(ASTNode):
    # type of the node
    type: Literal[NodeKind.BLOCK] = NodeKind.BLOCK

    # statements of the block
    statements: List["Node"] = Field(default_factory=list)

    def __str__(self):
        # get the string representation of the block
        body_str = " ".join(str(stmt) for stmt in self.statements)

        # return the string representation of the object
        return f"begin [body: {body_str}] end"

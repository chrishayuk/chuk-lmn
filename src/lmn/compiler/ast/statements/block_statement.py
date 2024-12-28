# file: lmn/compiler/ast/statements/block_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class BlockStatement(ASTNode):
    type: Literal[NodeKind.BLOCK] = NodeKind.BLOCK

    statements: List["Node"] = Field(default_factory=list)

    def __str__(self):
        body_str = " ".join(str(stmt) for stmt in self.statements)
        return f"begin [body: {body_str}] end"

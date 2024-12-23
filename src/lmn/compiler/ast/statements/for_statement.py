# lmn/compiler/ast/statements/for_statement.py
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.mega_union import MegaUnion

class ForStatement(ASTNode):
    type: Literal[NodeKind.FOR] = NodeKind.FOR

    # If 'variable' is truly an AST node (like a VariableExpression),
    # keep it as MegaUnion:
    variable: MegaUnion

    # Optional expressions:
    start_expr: Optional[MegaUnion] = None
    end_expr: Optional[MegaUnion] = None
    step_expr: Optional[MegaUnion] = None

    # The body can hold other statements or expressions (rare),
    # but usually it's statements:
    body: List[MegaUnion] = Field(default_factory=list)

    def __str__(self):
        step_part = f" step {self.step_expr}" if self.step_expr else ""
        return (
            f"for {self.variable} {self.start_expr} to {self.end_expr}"
            f"{step_part} [body: {self.body}]"
        )

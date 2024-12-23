# lmn/compiler/ast/expressions/fn_expression.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.mega_union import MegaUnion

class FnExpression(ASTNode):
    type: Literal[NodeKind.FN] = NodeKind.FN
    name: MegaUnion
    arguments: List[MegaUnion] = Field(default_factory=list)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"

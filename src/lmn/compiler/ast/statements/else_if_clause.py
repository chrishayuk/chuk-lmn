# file: lmn/compiler/ast/statements/else_if_clause.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class ElseIfClause(ASTNode):
    """
    Represents a single 'elseif' block:
      elseif (condition) { body... }
    """
    type: Literal[NodeKind.ELSEIF] = NodeKind.ELSEIF
    condition: "Expression"
    body: List["Statement"] = Field(default_factory=list)

    # pydantic model config
    model_config = {
        "populate_by_name": True,
        "use_enum_values": True
    }

    def __str__(self):
        cond_str = str(self.condition)
        body_str = " ".join(str(st) for st in self.body)
        return f"elseif {cond_str} [body: {body_str}]"

# file: lmn/compiler/ast/statements/else_if_clause.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class ElseIfClause(ASTNode):
    """
    Represents a single 'elseif' block:
      elseif (condition) { body... }
    """
    # elseif node type
    type: Literal[NodeKind.ELSEIF] = NodeKind.ELSEIF

    # the condition and body
    condition: "Expression"
    body: List["Statement"] = Field(default_factory=list)

    # pydantic model config
    model_config = {
        "populate_by_name": True,
        "use_enum_values": True
    }

    def __str__(self):
        # get the string representation of the condition
        cond_str = str(self.condition)

        # get the string representation of the body
        body_str = " ".join(str(st) for st in self.body)

        # return the string representation of the object
        return f"elseif {cond_str} [body: {body_str}]"

# file: lmn/compiler/ast/statements/if_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class IfStatement(ASTNode):
    """
    Represents an 'if' statement with optional else body.
    e.g.:
      if (condition) { thenBody... } else { elseBody... }
    """
    type: Literal[NodeKind.IF] = NodeKind.IF
    condition: "Expression"
    then_body: List["Statement"] = Field(default_factory=list, alias="thenBody")
    else_body: List["Statement"] = Field(default_factory=list, alias="elseBody")

    # Pydantic config to handle aliases
    model_config = {
        "populate_by_name": True,  # allow specifying either then_body= or thenBody=
        "use_enum_values": True    # store NodeKind.IF as "IfStatement"
    }

    def __str__(self):
        cond_str = str(self.condition)
        then_str = " ".join(str(st) for st in self.then_body)
        else_str = " ".join(str(st) for st in self.else_body)
        if else_str:
            return f"if {cond_str} [then: {then_str}] [else: {else_str}]"
        else:
            return f"if {cond_str} [then: {then_str}]"

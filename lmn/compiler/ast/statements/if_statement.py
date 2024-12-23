# compiler/ast/statements/if_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from compiler.ast.ast_node import ASTNode
from compiler.ast.node_kind import NodeKind
from compiler.ast.mega_union import MegaUnion

class IfStatement(ASTNode):
    type: Literal[NodeKind.IF] = NodeKind.IF

    condition: MegaUnion
    then_body: List[MegaUnion] = Field(default_factory=list, alias="thenBody")
    else_body: List[MegaUnion] = Field(default_factory=list, alias="elseBody")

    model_config = {
        "populate_by_name": True,  # allow specifying either then_body= or thenBody=
        "use_enum_values": True    # store NodeKind.IF as "IfStatement"
        # If you still see "then_body" in your dict output, try `by_alias=True` explicitly
    }

    def __str__(self):
        cond_str = str(self.condition)
        then_str = " ".join(str(st) for st in self.then_body)
        else_str = " ".join(str(st) for st in self.else_body)
        if else_str:
            return f"if {cond_str} [then: {then_str}] [else: {else_str}]"
        else:
            return f"if {cond_str} [then: {then_str}]"

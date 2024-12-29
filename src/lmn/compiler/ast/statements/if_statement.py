# file: lmn/compiler/ast/statements/if_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.statements.else_if_clause import ElseIfClause

class IfStatement(ASTNode):
    """
    Represents an 'if' statement with optional else and multiple elseif blocks:
      if (condition) { thenBody... }
      elseif (cond2) { elseifBody... }
      ...
      else { elseBody... }
    """
    type: Literal[NodeKind.IF] = NodeKind.IF
    condition: "Expression"
    then_body: List["Statement"] = Field(default_factory=list, alias="thenBody")
    elseif_clauses: List[ElseIfClause] = Field(default_factory=list, alias="elseifClauses")
    else_body: List["Statement"] = Field(default_factory=list, alias="elseBody")

    model_config = {
        "populate_by_name": True,  # allows either then_body= or thenBody=
        "use_enum_values": True
    }

    def __str__(self):
        cond_str = str(self.condition)
        then_str = " ".join(str(st) for st in self.then_body)
        elseif_strs = " ".join(str(elifc) for elifc in self.elseif_clauses)
        else_str = " ".join(str(st) for st in self.else_body)

        pieces = [f"if {cond_str} [then: {then_str}]"]
        if elseif_strs:
            pieces.append(elseif_strs)
        if else_str:
            pieces.append(f"else [body: {else_str}]")
        return " ".join(pieces)

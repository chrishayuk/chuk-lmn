# file: lmn/compiler/ast/statements/call_statement.py
from __future__ import annotations
from typing import List, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class CallStatement(StatementBase):
    """
    Represents: call "someTool" expr1 expr2 ...
    """
    type: Literal["CallStatement"] = "CallStatement"
    tool_name: str

    # arguments
    arguments: List["Expression"] = Field(default_factory=list)

    def __str__(self):
        args_str = " ".join(str(arg) for arg in self.arguments)
        return f'call "{self.tool_name}" {args_str}'

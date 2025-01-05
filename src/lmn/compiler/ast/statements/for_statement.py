# file: lmn/compiler/ast/statements/for_statement.py
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import Field

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class ForStatement(StatementBase):
    """
    Represents a 'for' loop, e.g.:
      for <variable> <start_expr> to <end_expr> step <step_expr> { ...body... }
    """
    type: Literal["ForStatement"] = "ForStatement"

    # If 'variable' might be a VariableExpression or other node, use a forward ref:
    variable: "Expression"

    # Optionally, if the start/end/step are expressions, also forward ref:
    start_expr: Optional["Expression"] = None
    end_expr: Optional["Expression"] = None
    step_expr: Optional["Expression"] = None

    # The body can hold other statements or expressions, so also forward ref:
    body: List["Node"] = Field(default_factory=list)

    def __str__(self):
        step_part = f" step {self.step_expr}" if self.step_expr else ""
        return (
            f"for {self.variable} {self.start_expr} to {self.end_expr}"
            f"{step_part} [body: {self.body}]"
        )

# file: lmn/compiler/ast/statements/break_statement.py
from __future__ import annotations
from typing import Literal

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class BreakStatement(StatementBase):
    """
    Represents a 'break' statement.
    """
    type: Literal["BreakStatement"] = "BreakStatement"

    def __str__(self):
        return "break"

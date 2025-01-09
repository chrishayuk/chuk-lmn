# file: lmn/compiler/ast/statements/continue_statement.py
from __future__ import annotations
from typing import Literal

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class ContinueStatement(StatementBase):
    """
    Represents a 'continue' statement.
    """
    type: Literal["ContinueStatement"] = "ContinueStatement"

    def __str__(self):
        return "continue"

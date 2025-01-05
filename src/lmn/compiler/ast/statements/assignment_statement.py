# file: lmn/compiler/ast/statements/assignment_statement.py
from __future__ import annotations
from typing import Literal, Optional

# lmn imports
from lmn.compiler.ast.statements.statement_base import StatementBase

class AssignmentStatement(StatementBase):
    # define the model configuration
    type: Literal["AssignmentStatement"] = "AssignmentStatement"

    # <- string name for the left-hand side
    variable_name: str  

    # or some expression type
    expression: "Expression"

    # optional field for inferred type
    inferred_type: Optional[str] = None

    def __str__(self):
        # output the node as a string
        return f"{self.variable_name} = {self.expression}"

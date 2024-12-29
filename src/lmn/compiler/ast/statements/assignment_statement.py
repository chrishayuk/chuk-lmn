# file: lmn/compiler/ast/statements/assignment_statement.py
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class AssignmentStatement(ASTNode):
    type: Literal[NodeKind.ASSIGNMENTSTATEMENT] = NodeKind.ASSIGNMENTSTATEMENT
    variable_name: str  # <- string name for the left-hand side
    expression: "Expression"  # or some expression type

    def __str__(self):
        return f"{self.variable_name} = {self.expression}"

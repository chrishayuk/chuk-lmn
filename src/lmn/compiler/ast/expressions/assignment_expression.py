# file: lmn/compiler/ast/expressions/assignment_expression.py
from __future__ import annotations
from typing import Literal, Optional

# lmn imports
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class AssignmentExpression(ExpressionBase):
    """
    An assignment expression node, e.g. (a = b) in expression context.
    If your parser transforms compound assignments (a += b) into
    something like (a = (a + b)), then the 'operator' may not be needed here.
    """
    # Use the NodeKind enum member for assignment expressions
    type: Literal[NodeKind.ASSIGNMENTEXPRESSION] = NodeKind.ASSIGNMENTEXPRESSION

    # The left side (often a variable or lvalue)
    left: "Expression"

    # The right side (any expression)
    right: "Expression"

    # Optional if you do type inference
    inferred_type: Optional[str] = None

    def __str__(self):
        # Return the string representation of the assignment expression
        return f"({self.left} = {self.right})"

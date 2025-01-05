# file: lmn/compiler/ast/statements/return_statement.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal

# lmn imports
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.statements.statement_base import StatementBase

# Only import Expression when type checking,
# so at runtime we avoid a potential circular import or missing definition.
if TYPE_CHECKING:
    # Adjust the path as needed to where you define Expression
    from lmn.compiler.ast.mega_union import Expression

class ReturnStatement(StatementBase):
    """
    Represents a 'return' statement, optionally returning an expression.
    e.g. return expr
    """
    type: Literal["ReturnStatement"] = "ReturnStatement"

    # Now we reference ExpressionBase (or your union) directly
    # instead of a string. Because of `if TYPE_CHECKING:`,
    # Python won't do a runtime import that might cause cycles.
    expression: Optional[Expression] = None

    def __str__(self):
        return f"return {self.expression}"

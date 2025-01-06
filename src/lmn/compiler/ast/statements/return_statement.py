# file: lmn/compiler/ast/statements/return_statement.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal

from lmn.compiler.ast.statements.statement_base import StatementBase

if TYPE_CHECKING:
    # Import the union of expression types only when type-checking,
    # preventing circular imports at runtime.
    from lmn.compiler.ast.mega_union import Expression


class ReturnStatement(StatementBase):
    """
    Represents a 'return' statement, optionally returning an expression.
    e.g. return expr
    """
    # The 'type' field is used by Pydantic's discriminated union logic
    type: Literal["ReturnStatement"] = "ReturnStatement"

    # Instead of 'Optional[str]', 'dict', or a partial type, we reference
    # 'Expression' from mega_union.py. This ensures Pydantic sees the sub-node
    # as a discriminated union, parsing it into a real node (BinaryExpression, etc.).
    expression: Optional["Expression"] = None

    def __str__(self) -> str:
        return f"return {self.expression}"
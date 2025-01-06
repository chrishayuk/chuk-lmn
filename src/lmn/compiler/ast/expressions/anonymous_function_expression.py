# file: lmn/compiler/ast/expressions/anonymous_function_expression.py
from __future__ import annotations
import logging
from typing import List, Literal, Optional, Tuple, TYPE_CHECKING
from pydantic import Field

# lmn
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

if TYPE_CHECKING:
    # We only import 'Statement' at type-check time to avoid circular imports at runtime
    from lmn.compiler.ast.mega_union import Statement

logger = logging.getLogger(__name__)

class AnonymousFunctionExpression(ExpressionBase):
    """
    Represents an inline anonymous function in the AST. For example:

        function(a, b)
            return a + b
        end

    or with types:

        function(a: int, b: int) : int
            return a + b
        end
    """

    type: Literal["AnonymousFunction"] = "AnonymousFunction"

    parameters: List[Tuple[str, Optional[str]]] = Field(default_factory=list)
    return_type: Optional[str] = None

    # Use the string-based forward reference and rely on model_rebuild()
    body: List["Statement"] = Field(default_factory=list)

    def __str__(self) -> str:
        logger.debug(
            "Entering AnonymousFunctionExpression.__str__ with parameters=%s, return_type=%s",
            self.parameters, self.return_type
        )

        # Build the parameter portion: e.g. "a:int, b:int"
        params_str = ", ".join(
            f"{name}:{ptype}" if ptype else name
            for (name, ptype) in self.parameters
        )

        # Build a string for the body statements
        body_str = "\n    ".join(str(stmt) for stmt in self.body)
        if body_str:
            body_str = f"\n    {body_str}\n"

        # If there's a return type, e.g. " : int"
        rtype_str = f": {self.return_type}" if self.return_type else ""

        func_str = f"function({params_str}){rtype_str} {{{body_str}}}"
        logger.debug("Exiting AnonymousFunctionExpression.__str__ with: %s", func_str)
        return func_str
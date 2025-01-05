# file: lmn/compiler/ast/expressions/anonymous_function_expression.py
from __future__ import annotations
import logging
from typing import List, Literal, Optional, Tuple
from pydantic import Field

# lmn
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.statements.statement_base import StatementBase

# logger
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

    # 1) Use a string literal for type, so Pydantic just stores "AnonymousFunction"
    type: Literal["AnonymousFunction"] = "AnonymousFunction"

    # 2) parameters: e.g. a list of (name, typeAnnotation)
    parameters: List[Tuple[str, Optional[str]]] = Field(default_factory=list)

    # 3) optional return type (like "int", "string", etc.)
    return_type: Optional[str] = None

    # 4) Body is a list of statements
    #    We reference 'StatementBase' as a string, so Python doesn't fail at import time
    body: List[StatementBase] = Field(default_factory=list)

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

    def to_dict(self) -> dict:
        logger.debug("AnonymousFunctionExpression.to_dict() called on: %s", self)

        # Build a dictionary by hand
        # Instead of relying on self.model_dump()
        result = {
            "type": self.type,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "body": []
        }

        # For each statement in the body, try to call `stmt.to_dict()` if available
        # otherwise fall back to a string representation
        for stmt in self.body:
            if hasattr(stmt, "to_dict") and callable(stmt.to_dict):
                result["body"].append(stmt.to_dict())
            else:
                # worst case, convert to string
                result["body"].append(str(stmt))

        logger.debug("AnonymousFunctionExpression.to_dict() => %s", result)
        return result
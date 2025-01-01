# file: lmn/compiler/ast/expressions/literal_expression.py
from __future__ import annotations
from typing import Union, Optional, Literal
from pydantic import BaseModel
from lmn.compiler.ast.node_kind import NodeKind
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.lexer.token import Token

class LiteralExpression(ExpressionBase):
    """
    Represents a literal value in the AST:
      - Integers (i32, i64)
      - Floats (f32, f64)
      - Strings
    """

    type: Literal[NodeKind.LITERAL] = NodeKind.LITERAL
    value: Union[int, float, str]   # The Python representation of the literal
    literal_type: Optional[str] = None  # e.g. "i32", "i64", "f32", "f64", "string"

    @classmethod
    def from_token(cls, token: Token) -> LiteralExpression:
        """
        Create a LiteralExpression from a lexer Token.
        This preserves the numeric kind (float, double, int, long) or sets to 'string'.
        """
        if token.token_type == LmnTokenType.INT_LITERAL:
            # 32-bit integer
            return cls(value=token.value, literal_type="int")

        elif token.token_type == LmnTokenType.LONG_LITERAL:
            # 64-bit integer
            return cls(value=token.value, literal_type="long")

        elif token.token_type == LmnTokenType.FLOAT_LITERAL:
            # 32-bit float
            return cls(value=token.value, literal_type="float")

        elif token.token_type == LmnTokenType.DOUBLE_LITERAL:
            # 64-bit float/double
            return cls(value=token.value, literal_type="double")

        elif token.token_type == LmnTokenType.STRING:
            return cls(value=token.value, literal_type="string")

        else:
            # Fallback for anything else (e.g., booleans or unknown)
            # Adapt if you have separate tokens for TRUE/FALSE, or NIL
            return cls(value=str(token.value), literal_type="string")

    def __str__(self) -> str:
        """
        A simple string representation—optional, for debugging.
        Could show the literal_type as well if desired.
        """
        return f"{self.value} (type={self.literal_type})"

# file: lmn/compiler/ast/expressions/literal_expression.py
from __future__ import annotations
import decimal
from typing import Optional, Union, Literal
from pydantic import model_validator

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

class LiteralExpression(ExpressionBase):
    """
    A literal value node (int, float, or string).
    """
    type: Literal[NodeKind.LITERAL] = NodeKind.LITERAL
    value: Union[int, float, str]
    inferred_type: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def convert_value(cls, values: dict) -> dict:
        raw_val = values.get("value")
        # If raw_val is already int or float, leave it alone.
        # If raw_val is a string that might be '3.14' or '42', parse:
        if isinstance(raw_val, str):
            try:
                # If '3.14' => float(3.14) => 3.14
                # If '42' => int(42)
                # If '42.0' => float(42.0) => 42.0
                # up to you whether to do .is_integer() or not
                possible_float = float(raw_val)
                if '.' in raw_val or 'e' in raw_val:
                    values["value"] = possible_float
                else:
                    values["value"] = int(raw_val)
            except ValueError:
                # not numeric
                pass
        return values


    def __str__(self):
        return str(self.value)

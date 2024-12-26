# file: lmn/compiler/ast/expressions/literal_expression.py
from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import model_validator

# import ast's
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

class LiteralExpression(ExpressionBase):
    """ A literal value node (int, float, or string). """
    type: Literal[NodeKind.LITERAL] = NodeKind.LITERAL
    value: Union[int, float, str]
    inferred_type: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def convert_value(cls, values: dict) -> dict:
        raw_val = values.get("value")

        if isinstance(raw_val, str):
            try:
                possible_float = float(raw_val)
                if possible_float.is_integer():
                    int_val = int(possible_float)
                    if int_val > 2147483647 or int_val < -2147483648:
                        # It's beyond 32-bit range, so set inferred_type to i64
                        values["inferred_type"] = "i64"
                    values["value"] = int_val
                else:
                    values["value"] = possible_float
            except ValueError:
                # not numeric, leave as string
                pass

        return values

    def __str__(self):
        return str(self.value)

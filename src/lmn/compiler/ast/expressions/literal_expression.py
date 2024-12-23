# lmn/compiler/ast/expressions/literal_expression.py
from __future__ import annotations
import decimal
from typing import Union, Literal
from pydantic import model_validator

from lmn.compiler.ast.ast_node import ASTNode
from lmn.compiler.ast.node_kind import NodeKind

class LiteralExpression(ASTNode):
    """
    A literal value node (int, float, or string).
    """
    type: Literal[NodeKind.LITERAL] = NodeKind.LITERAL
    value: Union[int, float, str]

    @model_validator(mode="before")
    def convert_value(cls, values):
        raw_val = values.get("value", None)
        if raw_val is not None:
            try:
                dec = decimal.Decimal(str(raw_val))
                if dec % 1 == 0:
                    values["value"] = int(dec)
                else:
                    values["value"] = float(dec)
            except (decimal.InvalidOperation, ValueError):
                if not isinstance(raw_val, str):
                    values["value"] = str(raw_val)
        return values

    def __str__(self):
        return str(self.value)

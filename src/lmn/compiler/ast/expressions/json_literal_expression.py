# file: lmn/compiler/ast/expressions/json_literal_expression.py
from __future__ import annotations
from typing import Any, Literal

# lmn imports
from lmn.compiler.ast.expressions.expression_base import ExpressionBase

class JsonLiteralExpression(ExpressionBase):
    """ 
    A literal node for JSON data (object, array, string, number, bool, or null).
    
    'value' will be a Python data structure:
      - dict for JSON objects
      - list for JSON arrays
      - str for string
      - int/float for number
      - bool for true/false
      - None for null
    """
    # set the type as json_literal
    type: Literal["JsonLiteralExpression"] = "JsonLiteralExpression"

    # value can be anything
    value: Any  # Or more specifically: Union[dict, list, str, int, float, bool, None]

    def __str__(self):
        # Return the string representation of the JSON literal expression
        return f"JsonLiteral({repr(self.value)})"

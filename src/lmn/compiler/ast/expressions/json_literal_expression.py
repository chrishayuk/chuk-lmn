# file: lmn/compiler/ast/expressions/json_literal_expression.py
from __future__ import annotations
from typing import Any, Literal
from lmn.compiler.ast.expressions.expression_base import ExpressionBase
from lmn.compiler.ast.node_kind import NodeKind

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
    type: Literal[NodeKind.JSON_LITERAL] = NodeKind.JSON_LITERAL
    value: Any  # Or more specifically: Union[dict, list, str, int, float, bool, None]

    def __str__(self):
        return f"JsonLiteral({repr(self.value)})"

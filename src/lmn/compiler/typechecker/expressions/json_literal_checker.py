# file: lmn/compiler/typechecker/json_literal_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 1) JSON Literal
# -------------------------------------------------------------------------

class JsonLiteralChecker(BaseExpressionChecker):
    def check(self, expr: JsonLiteralExpression, target_type: Optional[str] = None) -> str:
        # inferred type is json
        expr.inferred_type = "json"

        # return json
        return "json"

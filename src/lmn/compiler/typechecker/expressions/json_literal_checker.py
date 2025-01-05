# file: lmn/compiler/typechecker/json_literal_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

class JsonLiteralChecker(BaseExpressionChecker):
    def check(
        self,
        expr: JsonLiteralExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a JSON literal (like { "key": "value" } or [1,2,3]).
        Currently, we simply mark its inferred type as 'json'.

        :param expr: The JSON literal AST node.
        :param target_type: An optional 'hinted' type (e.g., if assigned to a variable of type 'json').
        :param local_scope: A local scope, if available (unused here, but provided for consistency).
        :return: Always returns 'json'.
        """
        # Inferred type is always 'json' for JSON literals
        expr.inferred_type = "json"

        # Return "json"
        return "json"

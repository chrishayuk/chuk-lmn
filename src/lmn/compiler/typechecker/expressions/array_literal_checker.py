# file: lmn/compiler/typechecker/array_literal_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 2) Array Literal
# -------------------------------------------------------------------------

class ArrayLiteralChecker(BaseExpressionChecker):
    def check(self, expr: ArrayLiteralExpression, target_type: Optional[str] = None) -> str:
        # check each element
        for elem in expr.elements:
            # check expression
            self.dispatcher.check_expression(elem)

        # infer type of array
        expr.inferred_type = "array"

        # return inferred type
        return "array"
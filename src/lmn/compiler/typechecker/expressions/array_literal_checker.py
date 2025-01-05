# file: lmn/compiler/typechecker/array_literal_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

class ArrayLiteralChecker(BaseExpressionChecker):
    def check(
        self,
        expr: ArrayLiteralExpression,
        target_type: Optional[str] = None,
        local_scope: Dict[str, Any] = None
    ) -> str:
        """
        Type-check an ArrayLiteralExpression by checking each element in the array.
        
        Steps:
          1) For each element, call self.dispatcher.check_expression(...) with local_scope
          2) Set expr.inferred_type = "array" (or some refined type, if you do array unification)
          3) Return the inferred type (here, "array")
        """

        # 1) Check each element in the given local scope
        for elem in expr.elements:
            self.dispatcher.check_expression(
                elem,
                target_type=None,
                local_scope=local_scope
            )

        # 2) Infer or set the type of the array
        expr.inferred_type = "array"

        # 3) Return the inferred type
        return "array"

# file: lmn/compiler/typechecker/binary_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

class BinaryChecker(BaseExpressionChecker):
    def check(
        self,
        expr: BinaryExpression,
        target_type: Optional[str] = None,
        local_scope: Dict[str, Any] = None
    ) -> str:
        """
        Type-check a BinaryExpression (e.g., left + right).

        Steps:
          1) Check each operand in the given local scope.
          2) Unify the operand types to find a common result type.
          3) Insert ConversionExpressions if one side must be converted.
          4) Return the result type.
        """

        # 1) Determine the types of the left/right sub-expressions,
        #    passing local_scope so variables are resolved locally.
        left_type = self.dispatcher.check_expression(
            expr.left, target_type=None, local_scope=local_scope
        )
        right_type = self.dispatcher.check_expression(
            expr.right, target_type=None, local_scope=local_scope
        )

        # 2) Unify the types
        result_type = unify_types(left_type, right_type, for_assignment=False)

        # 3) Store the inferred type in the AST node
        expr.inferred_type = result_type

        # 4) If left doesn't match the result, insert a ConversionExpression
        if left_type and result_type and left_type != result_type:
            expr.left = ConversionExpression(
                source_expr=expr.left,
                from_type=left_type,
                to_type=result_type
            )

        # 5) If right doesn't match the result, convert it as well
        if right_type and result_type and right_type != result_type:
            expr.right = ConversionExpression(
                source_expr=expr.right,
                from_type=right_type,
                to_type=result_type
            )

        # 6) Return the common result type
        return result_type

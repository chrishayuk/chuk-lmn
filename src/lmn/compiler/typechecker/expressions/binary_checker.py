# file: lmn/compiler/typechecker/binary_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

# -------------------------------------------------------------------------
# 5) BinaryExpression
# -------------------------------------------------------------------------

class BinaryChecker(BaseExpressionChecker):
    def check(self, expr: BinaryExpression, target_type: Optional[str] = None) -> str:
        # get the types of the operands
        left_type = self.dispatcher.check_expression(expr.left)
        right_type = self.dispatcher.check_expression(expr.right)

        # unify the types
        result_type = unify_types(left_type, right_type, for_assignment=False)

        # set the inferred type
        expr.inferred_type = result_type

        # check that the types are compatible
        if left_type is not None and result_type is not None and left_type != result_type:
            # convert the left operand
            expr.left = ConversionExpression(
                source_expr=expr.left,
                from_type=left_type,
                to_type=result_type
            )

        # check that the types are compatible
        if right_type is not None and result_type is not None and right_type != result_type:
            # convert the right operand
            expr.right = ConversionExpression(
                source_expr=expr.right,
                from_type=right_type,
                to_type=result_type
            )

        # return the type of the expression
        return result_type
    
    

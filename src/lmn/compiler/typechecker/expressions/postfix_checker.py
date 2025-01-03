# file: lmn/compiler/typechecker/postfix_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 8) PostfixExpression
# -------------------------------------------------------------------------

class PostfixChecker(BaseExpressionChecker):
    def check(self, expr: PostfixExpression, target_type: Optional[str] = None) -> str:
        # get the type of the operand
        operand_type = self.dispatcher.check_expression(expr.operand)

        # get the operator
        operator = expr.operator  # '++' or '--'

        # check if the operand is a valid type for the operator
        if operand_type not in ("int", "long", "float", "double"):
            # raise an error if it is not
            raise TypeError(f"Cannot apply postfix '{operator}' to '{operand_type}'. Must be numeric.")
        
        # set the inferred type of the expression
        expr.inferred_type = operand_type

        # return the inferred type of the expression
        return operand_type
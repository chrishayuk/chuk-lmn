# file: lmn/compiler/typechecker/literal_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 6) UnaryExpression
# -------------------------------------------------------------------------

class UnaryChecker(BaseExpressionChecker):
    def check(self, expr: UnaryExpression, target_type: Optional[str] = None) -> str:
        # Check the type of the operand
        operand_type = self.dispatcher.check_expression(expr.operand)

        # Get the operator
        op = expr.operator

        # Check if the operand is compatible with the operator
        if op in ("+", "-"):
            # numeric operators
            if operand_type not in ("int", "long", "float", "double"):
                # cannot apply numeric operators to non-numeric types
                raise TypeError(f"Cannot apply unary '{op}' to '{operand_type}'. Must be numeric.")
            
            # numeric operators are always compatible with themselves
            result_type = operand_type

        # boolean operators
        elif op == "not":
            # boolean operators
            if operand_type != "int":
                # 
                raise TypeError(f"Cannot apply 'not' to '{operand_type}'. Expecting 'int' as boolean.")
            
            # boolean operators are always compatible with themselves
            result_type = "int"

        else:
            # unknown/unimplemented operator
            raise NotImplementedError(f"Unknown unary operator '{op}'")
        
        # set the inferred type of the expression
        expr.inferred_type = result_type

        # return the type of the expression
        return result_type
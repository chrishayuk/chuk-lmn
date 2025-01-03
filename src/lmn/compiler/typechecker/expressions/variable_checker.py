# file: lmn/compiler/typechecker/variable_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 4) VariableExpression
# -------------------------------------------------------------------------

class VariableChecker(BaseExpressionChecker):
    def check(self, expr: VariableExpression, target_type: Optional[str] = None) -> str:
        # get the variable name
        var_name = expr.name

        # check that the variable name is in the symbol table
        if var_name not in self.symbol_table:
            # raise an error, variable used before assigned
            raise TypeError(f"Variable '{var_name}' used before assignment.")
        
        # get the type of the variable from the symbol table
        vtype = self.symbol_table[var_name]

        # set the inferred type of the expression
        expr.inferred_type = vtype

        # return the type
        return vtype

    
    

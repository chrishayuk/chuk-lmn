# file: lmn/compiler/typechecker/variable_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

# -------------------------------------------------------------------------
# 4) VariableExpression
# -------------------------------------------------------------------------

class VariableChecker(BaseExpressionChecker):
    def check(
        self,
        expr: VariableExpression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Type-check a VariableExpression (e.g. referencing a variable 'x').

        :param expr: The VariableExpression node (containing .name).
        :param target_type: An optional hinted type (typically for assignment).
        :param local_scope: A dictionary for local lookups if available;
                            otherwise self.symbol_table is used.
        :return: The inferred type of the variable (e.g. 'int').
        """
        # 1) Decide which scope to use
        scope = local_scope if local_scope is not None else self.symbol_table

        # 2) Get the variable name
        var_name = expr.name

        # 3) Check that the variable name is in the chosen scope
        if var_name not in scope:
            raise TypeError(f"Variable '{var_name}' used before assignment.")

        # 4) Retrieve the variable's type from the scope
        vtype = scope[var_name]

        # 5) Set the inferred type of the expression
        expr.inferred_type = vtype

        # 6) Return the type
        return vtype

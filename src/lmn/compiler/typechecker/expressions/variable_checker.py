# file: lmn/compiler/typechecker/variable_checker.py
from typing import Optional, Dict, Any
import logging

# lmn imports
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker

logger = logging.getLogger(__name__)

class VariableChecker(BaseExpressionChecker):
    """
    A checker for VariableExpression nodes, e.g. referencing a variable 'x'.
    """

    def __init__(self, expr_dispatcher, local_scope: Dict[str, Any]):
        """
        Overriding the constructor so we store the local_scope 
        that ExpressionDispatcher passes in.
        """
        super().__init__(expr_dispatcher, local_scope)
        self.local_scope = local_scope  # Save the effective local scope

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
        :param local_scope: [Ignored] We always use self.local_scope from the constructor.
        :return: The inferred type of the variable (e.g. 'int').
        """
        # 1) Always use self.local_scope set in the constructor
        #    (avoid local_scope param to prevent fallback to global symbol_table)
        scope = self.local_scope

        # 2) Get the variable name
        var_name = expr.name

        # 3) Debug: Print out scope info
        logger.debug(f"[VariableChecker] var_name='{var_name}'")
        logger.debug(f"[VariableChecker] scope keys = {list(scope.keys())}")
        assigned_vars = scope.get("__assigned_vars__", set())
        logger.debug(f"[VariableChecker] assigned_vars = {assigned_vars}")

        # 4) Check that the variable name is in the chosen scope
        if var_name not in scope:
            raise TypeError(f"Variable '{var_name}' used before assignment.")

        # 5) Retrieve the variable's type from the scope
        vtype = scope[var_name]
        logger.debug(f"[VariableChecker] Found var '{var_name}' => type='{vtype}'")

        # (Optional) If vtype is None, you can raise an error or unify it.

        # 6) Set the inferred type of the expression
        expr.inferred_type = vtype

        # 7) Return the type
        logger.debug(f"[VariableChecker] Returning type '{vtype}' for var '{var_name}'")
        return vtype

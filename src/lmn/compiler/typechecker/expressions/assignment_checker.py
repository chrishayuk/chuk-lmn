# file: lmn/compiler/typechecker/assignment_checker.py
from typing import Optional

# lmn imports
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

# -------------------------------------------------------------------------
# 7) AssignmentExpression
# -------------------------------------------------------------------------


class AssignmentChecker(BaseExpressionChecker):
    def check(self, expr: AssignmentExpression, target_type: Optional[str] = None) -> str:
        # Get LHS and RHS
        left_node = expr.left
        right_node = expr.right

        # Check LHS
        if not isinstance(left_node, VariableExpression):
            # Assignment LHS must be a variable
            raise TypeError(f"Assignment LHS must be a variable, got '{left_node.type}'")
        
        # Get variable name
        var_name = left_node.name

        # Check if variable is declared in symbol table
        right_type = self.dispatcher.check_expression(right_node)

        # Check if variable exists in symbol table
        if var_name in self.symbol_table:
            # Check if variable is already declared
            existing_type = self.symbol_table[var_name]

            # Unify types
            unified = unify_types(existing_type, right_type, for_assignment=True)

            # Update symbol table with new type
            self.symbol_table[var_name] = unified

            # Set the inferred type of the expression to be the unified type
            expr.inferred_type = unified
        else:
            # Declare on the fly
            self.symbol_table[var_name] = right_type

            # Set the inferred type of the expression to be the same as the RHS
            expr.inferred_type = right_type

        # return inferred type
        return expr.inferred_type
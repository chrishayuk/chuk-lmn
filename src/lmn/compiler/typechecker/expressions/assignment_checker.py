# file: lmn/compiler/typechecker/assignment_checker.py
from typing import Optional, Dict, Any

# lmn imports
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

class AssignmentChecker(BaseExpressionChecker):
    def check(
        self,
        expr: AssignmentExpression,
        target_type: Optional[str] = None,
        local_scope: Dict[str, Any] = None
    ) -> str:
        """
        Type-check an assignment expression of the form `a = some_expr`.

        Steps:
          1) Check that `expr.left` is a VariableExpression.
          2) Look up or create `var_name` in the local_scope or the global symbol table.
          3) Check the right-hand side expression with the local_scope.
          4) Unify the variable's existing type with the right-hand side's type.
          5) Update the scope and mark `var_name` as assigned.
          6) Return the unified (inferred) type.
        """

        # 1) Decide which scope to use
        scope = local_scope if local_scope is not None else self.symbol_table

        # 2) Validate LHS is a variable
        left_node = expr.left
        if not isinstance(left_node, VariableExpression):
            raise TypeError(
                f"Assignment LHS must be a variable, got '{left_node.type}'"
            )

        var_name = left_node.name

        # 3) Check the right-hand side expression
        right_type = self.dispatcher.check_expression(
            expr.right,
            target_type=None,
            local_scope=scope
        )

        # 4) See if 'var_name' is already in scope
        if var_name in scope:
            existing_type = scope[var_name]
            unified_type = unify_types(existing_type, right_type, for_assignment=True)
            scope[var_name] = unified_type
            expr.inferred_type = unified_type
        else:
            # Declare on the fly in the scope
            scope[var_name] = right_type
            expr.inferred_type = right_type

        # 5) Mark the variable as assigned in this scope
        assigned_vars = scope.get("__assigned_vars__", set())
        assigned_vars.add(var_name)
        scope["__assigned_vars__"] = assigned_vars

        # 6) Return the inferred type
        return expr.inferred_type

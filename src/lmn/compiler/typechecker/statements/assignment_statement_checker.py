# file: lmn/compiler/typechecker/statements/assignment_statement_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

class AssignmentStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker that handles
    type-checking for assignment statements (e.g. x = expression).
    """

    def check(self, assign_stmt, local_scope=None) -> None:
        """
        Type-check an assignment like: x = expression

        Steps:
          1) Confirm x is in the scope (local_scope or global symbol_table).
          2) Type-check the expression with the variable's type as a target hint.
          3) Unify or ensure compatibility with the variable's declared type.
          4) If needed, insert a ConversionExpression node (e.g. double->float).
          5) Update the scope with the new/unified type and mark variable as assigned.
        """
        logger.debug("Starting AssignmentStatementChecker...")

        # Determine which scope to use for lookups and assignments
        scope = local_scope if local_scope is not None else self.symbol_table

        # 1) variable_name
        var_name = getattr(assign_stmt, "variable_name", None)
        if var_name is None:
            logger.error("Assignment statement missing variable name")
            raise TypeError("Assignment statement missing variable name")

        # 2) Ensure the variable is declared in scope
        if var_name not in scope:
            logger.error(f"Variable '{var_name}' not declared before assignment")
            raise NameError(f"Variable '{var_name}' not declared before assignment")

        # 3) Check the expression type (pass the declared type as a 'hint')
        target_type = scope[var_name]
        logger.debug(f"Checking expression for var '{var_name}' => {assign_stmt.expression}")
        expr_type = self.dispatcher.check_expression(
            assign_stmt.expression, target_type=target_type, local_scope=scope
        )
        logger.debug(f"Expression type resolved to {expr_type}")

        # 4) Unify the existing var type with the expression's type
        existing_type = scope[var_name]
        new_type = unify_types(existing_type, expr_type, for_assignment=True)

        # 5) If we allow narrowing from "double" to "float", handle it:
        if existing_type == "float" and expr_type == "double":
            # Insert a ConversionExpression to narrow "double" -> "float"
            conv = ConversionExpression(
                source_expr=assign_stmt.expression,
                from_type="double",
                to_type="float"
            )
            assign_stmt.expression = conv
            new_type = "float"  # final type remains "float"

        # 6) Update the scope and the AST node
        scope[var_name] = new_type
        assign_stmt.inferred_type = new_type

        # 7) Mark variable as assigned in __assigned_vars__ (to avoid 'used before assignment' errors)
        assigned_vars = scope.get("__assigned_vars__", set())
        assigned_vars.add(var_name)
        scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            f"Finished assignment check: var '{var_name}' is now type '{new_type}'"
        )

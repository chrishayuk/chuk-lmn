# file: lmn/compiler/typechecker/statements/assignment_statement.py
import logging
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

def check_assignment_statement(assign_stmt, symbol_table: dict, dispatcher) -> None:
    """
    For a statement like: x = expression
    1) Confirm x is in the symbol table.
    2) Type-check the expression.
    3) Unify or ensure compatibility with the variable's declared type.
    4) If needed, insert a ConversionExpression node for narrowing or promotion.
    """
    logger.debug("Starting check_assignment_statement...")

    # 1. variable_name
    var_name = getattr(assign_stmt, "variable_name", None)
    if var_name is None:
        logger.error("Assignment statement missing variable name")
        raise TypeError("Assignment statement missing variable name")

    # 2. Ensure the variable is declared
    if var_name not in symbol_table:
        logger.error(f"Variable '{var_name}' not declared before assignment")
        raise NameError(f"Variable '{var_name}' not declared before assignment")

    # 3. Check the expression type (pass the declared type as a 'target_type')
    target_type = symbol_table[var_name]
    logger.debug(f"Checking expression for var '{var_name}' => {assign_stmt.expression}")
    expr_type = dispatcher.check_expression(assign_stmt.expression, target_type)
    logger.debug(f"Expression type resolved to {expr_type}")

    # 4. Unify the existing var type (e.g. "int", "float") with the expression's type
    existing_type = symbol_table[var_name]
    new_type = unify_types(existing_type, expr_type, for_assignment=True)

    # 5. If we allow narrowing from "double" to "float", handle it similarly:
    if existing_type == "float" and expr_type == "double":
        from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
        # Insert a ConversionExpression to narrow "double" -> "float"
        conv = ConversionExpression(
            source_expr=assign_stmt.expression,
            from_type="double",
            to_type="float"
        )
        assign_stmt.expression = conv
        new_type = "float"  # final type remains "float"

    # 6. Update the symbol table and the AST node
    symbol_table[var_name] = new_type
    assign_stmt.inferred_type = new_type

    logger.debug(f"Finished assignment check: var '{var_name}' is now type '{new_type}'")

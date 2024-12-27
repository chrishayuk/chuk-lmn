# file: lmn/compiler/typechecker/statements/assignment_statement.py
import logging
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.utils import unify_types

# setup the logger
logger = logging.getLogger(__name__)

def check_assignment_statement(assign_stmt, symbol_table: dict) -> None:
    """
    For statement like: x = expression
    We'll confirm x is in the symbol table, typecheck the expression, and unify or ensure compatibility.
    """
    logger.debug("Starting check_assignment_statement...")

    # 1. variable_name or variable expression
    var_name = getattr(assign_stmt, "variable_name", None)

    # check if variable name is present
    if var_name is None:
        # variable name is missing
        logger.error("Assignment statement missing variable name")
        raise TypeError("Assignment statement missing variable name")

    # 2. Ensure variable exists in symbol table
    if var_name not in symbol_table:
        # variable not found in the symbol table
        logger.error(f"Variable '{var_name}' not declared before assignment")
        raise NameError(f"Variable '{var_name}' not declared before assignment")

    # Get the target type for the assignment
    target_type = symbol_table[var_name]

    # 3. Check the expression type, passing the target type
    logger.debug(f"Checking expression for var '{var_name}' => {assign_stmt.expression}")
    expr_type = check_expression(assign_stmt.expression, symbol_table, target_type)
    logger.debug(f"Expression type resolved to {expr_type}")

    # 4. Unify with existing
    existing_type = symbol_table[var_name]
    new_type = unify_types(existing_type, expr_type, for_assignment=True) # Ensure assignment rules are followed
    symbol_table[var_name] = new_type

    # 5. Optionally store an inferred_type on the node
    assign_stmt.inferred_type = new_type

    # debug
    logger.debug(f"Finished assignment check: var '{var_name}' is now type '{new_type}'")
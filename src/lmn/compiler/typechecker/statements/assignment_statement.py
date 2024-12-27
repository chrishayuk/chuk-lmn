# file: lmn/compiler/typechecker/statements/assignment_statement.py
import logging
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

def check_assignment_statement(assign_stmt, symbol_table: dict) -> None:
    """
    For statement like: x = expression
    We'll confirm x is in the symbol table, typecheck the expression, and unify or ensure compatibility.
    """
    logger.debug("Starting check_assignment_statement...")

    # 1. variable_name
    var_name = getattr(assign_stmt, "variable_name", None)
    if var_name is None:
        logger.error("Assignment statement missing variable name")
        raise TypeError("Assignment statement missing variable name")

    # 2. Check variable is declared
    if var_name not in symbol_table:
        logger.error(f"Variable '{var_name}' not declared before assignment")
        raise NameError(f"Variable '{var_name}' not declared before assignment")

    # 3. Check the expression type (pass the declared type as a hint)
    target_type = symbol_table[var_name]
    logger.debug(f"Checking expression for var '{var_name}' => {assign_stmt.expression}")
    expr_type = check_expression(assign_stmt.expression, symbol_table, target_type)
    logger.debug(f"Expression type resolved to {expr_type}")

    # 4. unify with existing
    existing_type = symbol_table[var_name]
    new_type = unify_types(existing_type, expr_type, for_assignment=True)

    # 4a. If the variable is f32 but the expression ended up as f64,
    #     we allow demotion => Insert a ConversionExpression node.
    if existing_type == "f32" and expr_type == "f64":
        from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
        # Wrap the original expr in a demotion node
        conv = ConversionExpression(
            source_expr=assign_stmt.expression,
            from_type="f64",
            to_type="f32"
        )
        assign_stmt.expression = conv
        new_type = "f32"  # final type is f32

    # 5. Store final type in symbol_table and the AST node
    symbol_table[var_name] = new_type
    assign_stmt.inferred_type = new_type

    logger.debug(f"Finished assignment check: var '{var_name}' is now type '{new_type}'")

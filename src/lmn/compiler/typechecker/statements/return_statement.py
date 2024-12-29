# file: lmn/compiler/typechecker/statements/return_statement.py

import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.utils import normalize_type, unify_types
from lmn.compiler.typechecker.expression_checker import check_expression

logger = logging.getLogger(__name__)

def check_return_statement(stmt, symbol_table: Dict[str, str]) -> None:
    """
    Type-check a return statement, verifying that the returned expression
    (if present) matches or can unify with the function's expected return type.
    If the function's return type is not yet declared, infer it from the first
    ReturnStatement we see.
    """

    expr = getattr(stmt, "expression", None)

    # See if we've already recorded a return type in __current_function_return_type__
    declared_return_type = symbol_table.get("__current_function_return_type__", None)
    logger.debug(f"Current function return type (before check): {declared_return_type}")

    # 1) If we have a return expression, check it
    if expr:
        expr_type = check_expression(expr, symbol_table)
        logger.debug(f"Return expression type: {expr_type}")

        if declared_return_type is not None:
            # We already have a declared/inferred return type => unify
            declared_norm = normalize_type(declared_return_type)
            expr_norm = normalize_type(expr_type)

            unified_type = unify_types(declared_norm, expr_norm, for_assignment=True)
            if unified_type != declared_norm:
                raise TypeError(
                    f"Return type mismatch: function expects '{declared_return_type}', "
                    f"but expression is '{expr_type}'."
                )

            stmt.inferred_type = declared_return_type
        else:
            # No declared return type yet => adopt this expression's type
            stmt.inferred_type = expr_type
            symbol_table["__current_function_return_type__"] = expr_type
            logger.debug(f"Inferred function return type as '{expr_type}'")

    # 2) If there's no expression => "return;" means void
    else:
        logger.debug("Return statement with no expression (i.e. return;).")
        if declared_return_type and declared_return_type != "void":
            # If the function already has an inferred or declared type that isn't void => mismatch
            raise TypeError(
                f"Return type mismatch: function expects '{declared_return_type}', "
                "but got no return value."
            )

        # Otherwise, adopt or confirm "void"
        stmt.inferred_type = "void"
        if declared_return_type is None:
            symbol_table["__current_function_return_type__"] = "void"
            logger.debug("Inferred function return type as 'void'.")

    logger.debug(f"Return statement check completed; inferred_type = {stmt.inferred_type}")
    logger.debug(f"Current function return type (after check): {symbol_table.get('__current_function_return_type__', None)}")

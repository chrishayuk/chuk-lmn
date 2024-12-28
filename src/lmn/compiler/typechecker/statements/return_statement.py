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
    Example:
      {
        "type": "ReturnStatement",
        "expression": { ... }  # AST for the returned expression, if any
      }
    """

    # 1) Retrieve the expression from the AST node (could be None).
    expr = getattr(stmt, "expression", None)

    # 2) Retrieve the declared function return type from the symbol table.
    #    You might store it under a special key when you enter the function's scope.
    declared_return_type = symbol_table.get("__current_function_return_type__", None)
    logger.debug(f"Declared function return type: {declared_return_type}")

    if expr:
        # 3) Type-check the return expression
        expr_type = check_expression(expr, symbol_table)
        logger.debug(f"Return expression type: {expr_type}")

        # 4) If there's a declared return type, unify or ensure they match
        if declared_return_type:
            # Possibly normalize both sides (if your language needs that).
            declared_norm = normalize_type(declared_return_type)
            expr_norm = normalize_type(expr_type)

            # Decide if you want `for_assignment=True` or `False`.
            # Typically for return statements, we treat the function's return type
            # as the 'target', so `for_assignment=True` can make sense if you allow
            # "up-conversion" or "down-conversion" automatically.
            #
            # But you may want to treat it as an exact match, in which case for_assignment=False
            # would be stricter:
            unified_type = unify_types(declared_norm, expr_norm, for_assignment=True)

            # If unification picks something other than declared_norm,
            # it means there's a mismatch or requires an explicit cast.
            if unified_type != declared_norm:
                raise TypeError(
                    f"Return type mismatch: function expects '{declared_return_type}', "
                    f"but expression is '{expr_type}'."
                )

            # Record that the statement's type is the declared return type
            stmt.inferred_type = declared_return_type
        else:
            # If there's no declared return type, we might be in a "dynamic" or
            # "implicit" scenario. We'll just store the expression's type for now.
            stmt.inferred_type = expr_type

        logger.debug(f"Return statement inferred type: {stmt.inferred_type}")
    else:
        # 5) No expression => check if the function is supposed to return void
        logger.debug("Return statement with no expression.")
        if declared_return_type and declared_return_type != "void":
            raise TypeError(
                f"Return type mismatch: function expects '{declared_return_type}', "
                "but got no return value."
            )
        # For a void function, it's valid to return nothing.
        stmt.inferred_type = "void"
        logger.debug("Marked return statement with type 'void'.")

    logger.debug("Return statement check completed.")

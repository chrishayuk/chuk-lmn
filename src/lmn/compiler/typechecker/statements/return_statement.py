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
          "expression": { ... }  # AST for the returned expression
        }
    """

    # 1) Retrieve the expression (could be None if you allow "return" with no expr).
    expr = getattr(stmt, "expression", None)

    # 2) If your parser or typechecker stores the *current function return type*
    #    in the symbol table, retrieve it. This is just an example:
    declared_return_type = symbol_table.get("__current_function_return_type__", None)
    logger.debug(f"Declared function return type: {declared_return_type}")

    if expr:
        # 3) Type-check the expression
        expr_type = check_expression(expr, symbol_table)
        logger.debug(f"Return expression type: {expr_type}")

        # 4) If a declared return type exists, unify or ensure compatibility
        if declared_return_type:
            # Normalize both sides to internal type format if needed
            unified_type = unify_types(
                normalize_type(declared_return_type), 
                normalize_type(expr_type),
                for_assignment=False  # or True, depending on your unify logic
            )

            if unified_type != normalize_type(declared_return_type):
                raise TypeError(
                    f"Return type mismatch: function expects '{declared_return_type}', got '{expr_type}'"
                )

            # If everything is fine, set the statement's inferred type
            stmt.inferred_type = declared_return_type
        else:
            # No declared type => The function might be implicitly typed
            # or a "dynamic" language scenario
            stmt.inferred_type = expr_type

        logger.debug(f"Return statement inferred type: {stmt.inferred_type}")
    
    else:
        # No expression. Possibly "return" in a void or unit function
        logger.debug("Return statement with no expression.")
        if declared_return_type and declared_return_type != "void":
            raise TypeError(
                f"Return type mismatch: function expects '{declared_return_type}', got no return value."
            )
        stmt.inferred_type = "void"  # or None, depending on your language

    logger.debug("Return statement check completed.")

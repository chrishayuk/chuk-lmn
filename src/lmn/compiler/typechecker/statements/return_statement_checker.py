# file: lmn/compiler/typechecker/statements/return_statement_checker.py
import logging
from typing import Dict

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

class ReturnStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker to handle type-checking
    for 'return' statements within functions.
    """

    def check(self, stmt, local_scope: Dict[str, str] = None) -> None:
        """
        Type-check a return statement in a function.

        If local_scope is provided, we use it for checking variable assignments
        and updating the function's return type. Otherwise, we fall back to
        self.symbol_table (the global one) — but typically, we want a local_scope
        inside a function body.
        """
        expr = getattr(stmt, "expression", None)

        # Decide which table to use
        scope = local_scope if local_scope is not None else self.symbol_table

        # The function's currently known or declared return type
        declared_return_type = scope.get("__current_function_return_type__", None)

        if expr:
            # 1) We have a return expression => type-check it
            logger.debug("Type-checking return expression.")
            # Pass the same scope when checking the expression
            expr_type = self.dispatcher.check_expression(expr, local_scope=scope)

            if declared_return_type is None:
                # No type known yet => adopt the expression's type
                logger.debug(f"No declared return type. Adopting type '{expr_type}'.")
                scope["__current_function_return_type__"] = expr_type
                stmt.inferred_type = expr_type
            else:
                # 2) We already have a declared return type => unify
                logger.debug(
                    f"Declared return type: '{declared_return_type}'. "
                    f"Return expression type: '{expr_type}'."
                )
                unified = unify_types(declared_return_type, expr_type, for_assignment=False)

                if unified != declared_return_type:
                    # If the old type was "void", adopt the new one
                    if declared_return_type == "void":
                        logger.debug(f"Updating return type from 'void' to '{expr_type}'.")
                        scope["__current_function_return_type__"] = expr_type
                        stmt.inferred_type = expr_type
                    else:
                        # Real mismatch => raise error
                        logger.error(
                            f"Return mismatch: function expects '{declared_return_type}', "
                            f"got '{expr_type}'"
                        )
                        raise TypeError(
                            f"Return mismatch: function expects '{declared_return_type}', "
                            f"got '{expr_type}'"
                        )
                else:
                    # unify == declared_return_type => OK
                    logger.debug(f"Return type matches declared type: '{declared_return_type}'.")
                    stmt.inferred_type = declared_return_type
        else:
            # 3) No return expression => unify with 'void'
            logger.debug("No return expression. Defaulting to 'void'.")
            if declared_return_type is None:
                # adopt 'void'
                scope["__current_function_return_type__"] = "void"
                stmt.inferred_type = "void"
            elif declared_return_type != "void":
                # The user returns "nothing" but we had a known non-void => mismatch
                logger.error(
                    f"Return mismatch: function expects '{declared_return_type}', got 'void'"
                )
                raise TypeError(
                    f"Return mismatch: function expects '{declared_return_type}', got 'void'"
                )
            else:
                # declared_return_type is already "void", so no problem
                stmt.inferred_type = "void"

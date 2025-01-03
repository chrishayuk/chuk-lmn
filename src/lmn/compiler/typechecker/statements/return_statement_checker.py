# file: lmn/compiler/typechecker/statements/return_statement_checker.py
import logging
from typing import Dict

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types

# logger
logger = logging.getLogger(__name__)

class ReturnStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker to handle type-checking
    for 'return' statements within functions.
    """

    def check(self, stmt) -> None:
        """
        Type-check a return statement in a function.
        """
        expr = getattr(stmt, "expression", None)

        # The function's currently known or declared return type
        declared_return_type = self.symbol_table.get("__current_function_return_type__", None)

        if expr:
            # 1) We have a return expression => type-check it
            logger.debug("Type-checking return expression.")
            expr_type = self.dispatcher.check_expression(expr)

            if declared_return_type is None:
                # No type known yet => adopt the expression's type
                logger.debug(f"No declared return type. Adopting type '{expr_type}'.")
                self.symbol_table["__current_function_return_type__"] = expr_type
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
                        self.symbol_table["__current_function_return_type__"] = expr_type
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
                self.symbol_table["__current_function_return_type__"] = "void"
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

# file: lmn/compiler/typechecker/statements/return_statement_checker.py

import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

class ReturnStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker to handle type-checking
    for 'return' statements within functions.
    """

    def check(
        self,
        stmt,
        local_scope: Dict[str, str] = None,
        function_return_type: Optional[str] = None
    ) -> str:
        """
        Type-checks a ReturnStatement node.

        :param stmt: The ReturnStatement node.
        :param local_scope: Local scope dictionary, including a 
                            '__current_function_return_type__' entry.
        :param function_return_type: The function's declared return type
                                    (e.g. "int", "void", or None if not declared).
        :return: The final inferred type for this ReturnStatement.
        """
        # Usually the statement includes an expression attribute.
        expr = getattr(stmt, "expression", None)
        scope = local_scope if local_scope is not None else self.symbol_table

        # ---------------------------------------------------------
        # CASE A: We have a return expression (e.g. return 1).
        # ---------------------------------------------------------
        if expr:
            logger.debug("ReturnStatementChecker: Type-checking return expression.")
            expr_type = self.dispatcher.check_expression(expr, local_scope=scope)

            # If function has no declared return type (None) or "void",
            # we adopt this expression's type (e.g., "int").
            if function_return_type is None or function_return_type == "void":
                logger.debug(f"No or 'void' declared return type => adopting '{expr_type}'.")

                # Update local scope so that FunctionDefinitionChecker
                # can finalize the function with the new type.
                scope["__current_function_return_type__"] = expr_type

                stmt.inferred_type = expr_type
                return expr_type

            # Otherwise, the user declared something like -> int,
            # so unify or raise error on mismatch.
            logger.debug(
                f"Declared return type: '{function_return_type}'. "
                f"Return expression type: '{expr_type}'."
            )
            unified = unify_types(function_return_type, expr_type, for_assignment=False)
            if unified != function_return_type:
                logger.error(
                    f"Return mismatch: function expects '{function_return_type}', got '{expr_type}'"
                )
                raise TypeError(
                    f"Return mismatch: function expects '{function_return_type}', got '{expr_type}'"
                )
            else:
                stmt.inferred_type = function_return_type
                return function_return_type

        # ---------------------------------------------------------
        # CASE B: We have a bare return statement (return;).
        # ---------------------------------------------------------
        else:
            logger.debug("ReturnStatementChecker: No return expression => 'void'.")
            # If the function is declared -> int, we raise an error.
            if function_return_type and function_return_type != "void":
                logger.error(
                    f"Return mismatch: function expects '{function_return_type}', got 'void'"
                )
                raise TypeError(
                    f"Return mismatch: function expects '{function_return_type}', got 'void'"
                )
            # Otherwise, the function is -> void or None => adopt "void".
            scope["__current_function_return_type__"] = "void"
            stmt.inferred_type = "void"
            return "void"

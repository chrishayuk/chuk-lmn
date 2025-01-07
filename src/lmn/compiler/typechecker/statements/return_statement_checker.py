# file: lmn/compiler/typechecker/statements/return_statement_checker.py

import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types
from pydantic import TypeAdapter

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
        function_return_type: Optional[str] = None  # <--- new param
    ) -> str:
        """
        Type-checks a ReturnStatement node.

        :param stmt: The ReturnStatement node (dict or typed node).
        :param local_scope: A dictionary for local variables and their types.
        :param function_return_type: The declared return type of the function,
                                     if known. E.g. "int", "void", or None.
        :return: The final inferred type of this ReturnStatement (often the same
                 as function_return_type, or the expression's type).
        :raises: TypeError if the return expression mismatches the function's declared type.
        """
        expr = getattr(stmt, "expression", None)

        # If 'expr' is a dict, parse it via the TypeAdapter for your union
        if isinstance(expr, dict):
            from lmn.compiler.ast.mega_union import Expression
            logger.debug("ReturnStatementChecker: converting expression from dict via TypeAdapter.")
            ta_expr = TypeAdapter(Expression)
            expr = ta_expr.validate_python(expr)
            stmt.expression = expr

        scope = local_scope if local_scope is not None else self.symbol_table

        if expr:
            # We have a return expression => type-check the expression
            logger.debug("ReturnStatementChecker: Type-checking return expression.")
            expr_type = self.dispatcher.check_expression(expr, local_scope=scope)

            if function_return_type is None:
                # If no declared return type => adopt the expression's type
                logger.debug(f"No declared return type => adopting '{expr_type}'.")
                stmt.inferred_type = expr_type
                return expr_type
            else:
                # We unify with function_return_type
                logger.debug(
                    f"Declared return type: '{function_return_type}'. "
                    f"Return expression type: '{expr_type}'."
                )
                unified = unify_types(function_return_type, expr_type, for_assignment=False)
                if unified != function_return_type:
                    # Mismatch => error
                    logger.error(
                        f"Return mismatch: function expects '{function_return_type}', got '{expr_type}'"
                    )
                    raise TypeError(
                        f"Return mismatch: function expects '{function_return_type}', got '{expr_type}'"
                    )
                else:
                    # Expression is compatible => return function_return_type
                    stmt.inferred_type = function_return_type
                    return function_return_type
        else:
            # No return expression => "void"
            logger.debug("ReturnStatementChecker: No return expression => 'void'.")
            if function_return_type and function_return_type != "void":
                logger.error(
                    f"Return mismatch: function expects '{function_return_type}', got 'void'"
                )
                raise TypeError(
                    f"Return mismatch: function expects '{function_return_type}', got 'void'"
                )
            stmt.inferred_type = "void"
            return "void"

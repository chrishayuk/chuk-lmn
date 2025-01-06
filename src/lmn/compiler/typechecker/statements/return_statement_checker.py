# file: lmn/compiler/typechecker/statements/return_statement_checker.py
import logging
from typing import Dict

from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types
from pydantic import TypeAdapter

logger = logging.getLogger(__name__)


class ReturnStatementChecker(BaseStatementChecker):
    """
    A subclass of BaseStatementChecker to handle type-checking
    for 'return' statements within functions.
    """

    def check(self, stmt, local_scope: Dict[str, str] = None) -> None:
        expr = getattr(stmt, "expression", None)

        # If 'expr' is a dict, parse it via the TypeAdapter for your union
        if isinstance(expr, dict):
            from lmn.compiler.ast.mega_union import Expression
            logger.debug("Expression is a dict; converting via TypeAdapter(Expression).validate_python()...")
            ta_expr = TypeAdapter(Expression)
            expr = ta_expr.validate_python(expr)
            stmt.expression = expr

        scope = local_scope if local_scope is not None else self.symbol_table
        declared_return_type = scope.get("__current_function_return_type__", None)

        if expr:
            logger.debug("Type-checking return expression.")
            expr_type = self.dispatcher.check_expression(expr, local_scope=scope)

            if declared_return_type is None:
                logger.debug(f"No declared return type. Adopting type '{expr_type}'.")
                scope["__current_function_return_type__"] = expr_type
                stmt.inferred_type = expr_type
            else:
                logger.debug(
                    f"Declared return type: '{declared_return_type}'. Return expression type: '{expr_type}'."
                )
                unified = unify_types(declared_return_type, expr_type, for_assignment=False)

                if unified != declared_return_type:
                    if declared_return_type == "void":
                        logger.debug(f"Updating return type from 'void' to '{expr_type}'.")
                        scope["__current_function_return_type__"] = expr_type
                        stmt.inferred_type = expr_type
                    else:
                        logger.error(
                            f"Return mismatch: function expects '{declared_return_type}', got '{expr_type}'"
                        )
                        raise TypeError(
                            f"Return mismatch: function expects '{declared_return_type}', got '{expr_type}'"
                        )
                else:
                    logger.debug(f"Return type matches declared type: '{declared_return_type}'.")
                    stmt.inferred_type = declared_return_type

        else:
            logger.debug("No return expression. Defaulting to 'void'.")
            if declared_return_type is None:
                scope["__current_function_return_type__"] = "void"
                stmt.inferred_type = "void"
            elif declared_return_type != "void":
                logger.error(
                    f"Return mismatch: function expects '{declared_return_type}', got 'void'"
                )
                raise TypeError(
                    f"Return mismatch: function expects '{declared_return_type}', got 'void'"
                )
            else:
                stmt.inferred_type = "void"

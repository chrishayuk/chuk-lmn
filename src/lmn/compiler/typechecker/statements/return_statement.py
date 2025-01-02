# file: lmn/compiler/typechecker/statements/return_statement.py

import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.utils import normalize_type, unify_types
from lmn.compiler.typechecker.expression_checker import check_expression

logger = logging.getLogger(__name__)

def check_return_statement(stmt, symbol_table: dict):
    expr = getattr(stmt, "expression", None)

    # The function's currently known or declared return type
    declared_return_type = symbol_table.get("__current_function_return_type__", None)

    if expr:
        # 1) We have a return expression => type-check it
        expr_type = check_expression(expr, symbol_table)

        if declared_return_type is None:
            # No type known yet => adopt the expression's type
            symbol_table["__current_function_return_type__"] = expr_type
            stmt.inferred_type = expr_type

        else:
            # 2) We already have a declared return type => unify
            unified = unify_types(declared_return_type, expr_type, for_assignment=False)

            if unified != declared_return_type:
                # If the old type was "void", adopt the new one
                if declared_return_type == "void":
                    symbol_table["__current_function_return_type__"] = expr_type
                    stmt.inferred_type = expr_type
                else:
                    # Real mismatch => raise error
                    raise TypeError(
                        f"Return mismatch: function expects {declared_return_type}, got {expr_type}"
                    )
            else:
                # unify == declared_return_type => OK
                stmt.inferred_type = declared_return_type

    else:
        # 3) No return expression => unify with 'void'
        if declared_return_type is None:
            # adopt 'void'
            symbol_table["__current_function_return_type__"] = "void"
            stmt.inferred_type = "void"

        elif declared_return_type != "void":
            # The user returns "nothing" but we had a known non-void => mismatch
            raise TypeError(
                f"Return mismatch: function expects {declared_return_type}, got void"
            )
        else:
            # declared_return_type is already "void", so no problem
            stmt.inferred_type = "void"


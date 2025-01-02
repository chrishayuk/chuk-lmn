# file: lmn/compiler/typechecker/statements/return_statement.py

import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.utils import normalize_type, unify_types
from lmn.compiler.typechecker.expression_checker import check_expression

logger = logging.getLogger(__name__)

def check_return_statement(stmt, symbol_table: dict):
    expr = getattr(stmt, "expression", None)
    # This is the function's currently known or declared return type
    declared_return_type = symbol_table.get("__current_function_return_type__", None)

    if expr:
        expr_type = check_expression(expr, symbol_table)

        if declared_return_type is None:
            # adopt the expression's type
            symbol_table["__current_function_return_type__"] = expr_type
            stmt.inferred_type = expr_type
        else:
            # unify
            unified = unify_types(declared_return_type, expr_type, for_assignment=False)
            if unified != declared_return_type:
                raise TypeError(f"Return mismatch: function expects {declared_return_type}, got {expr_type}")
            stmt.inferred_type = declared_return_type
    else:
        # No return expression => unify with 'void'
        if declared_return_type is None:
            symbol_table["__current_function_return_type__"] = "void"
            stmt.inferred_type = "void"
        elif declared_return_type != "void":
            raise TypeError(...)
        else:
            stmt.inferred_type = "void"

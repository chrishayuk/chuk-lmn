# file: lmn/compiler/typechecker/statements/let_statement.py
import logging
from typing import Dict, Optional

from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.utils import normalize_type, unify_types

logger = logging.getLogger(__name__)

def check_let_statement(stmt, symbol_table: Dict[str, str]) -> None:
    """
    Type check a 'let' statement and update the symbol table. Example:
      let x: int = 5
      let y
      let ratio: float
      let eVal: double = 2.718
    """
    var_name = stmt.variable.name
    type_annotation = stmt.type_annotation  # e.g. "int", "float", ...
    expr = stmt.expression

    logger.debug(f"Processing 'let' statement for variable '{var_name}'")
    logger.debug(f"Type annotation: {type_annotation}")

    # Convert type_annotation to your language-level format if needed
    declared_type = normalize_type(type_annotation) if type_annotation else None

    if expr:
        # There's an initializer expression, so type-check it with declared_type as a hint
        logger.debug(f"Type-checking expression for variable '{var_name}'.")
        expr_type = check_expression(expr, symbol_table, declared_type)
        logger.debug(f"Expression type for '{var_name}' resolved to {expr_type}")

        if declared_type:
            # Ensure assignment compatibility: declared_type = expr_type
            unified_type = unify_types(declared_type, expr_type, for_assignment=True)
            if unified_type != declared_type:
                # If unify_types picks something other than declared_type,
                # it means the assignment isn't valid (or needs an explicit cast).
                raise TypeError(
                    f"Cannot assign '{expr_type}' to variable of type '{declared_type}'"
                )
            # If it is valid, we just keep declared_type
            final_type = declared_type
        else:
            # No declared type, so we take whatever the expression's type is
            final_type = expr_type

        # Update symbol table: var_name -> final_type
        symbol_table[var_name] = final_type

        # Mark 'stmt' and 'stmt.variable' with final_type
        stmt.inferred_type = final_type
        stmt.variable.inferred_type = final_type

        logger.debug(f"Added '{var_name}' with type {final_type} to the symbol table.")

    else:
        # No initializer expression
        logger.debug(f"No expression provided in 'let' statement for '{var_name}'.")
        # If no declared_type either, that might be a separate error or default
        if not declared_type:
            raise TypeError(
                f"No type annotation or initializer for variable '{var_name}' in let statement."
            )

        # Just add declared_type to the symbol table
        symbol_table[var_name] = declared_type
        stmt.variable.inferred_type = declared_type
        stmt.inferred_type = declared_type  # In case you want to store the type at the statement level as well

        logger.debug(f"Marking '{var_name}' with type '{declared_type}' in the symbol table.")

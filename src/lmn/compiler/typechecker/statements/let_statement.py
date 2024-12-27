# file: lmn/compiler/typechecker/statements/let_statement.py
import logging
from typing import Dict, Optional
from lmn.compiler.typechecker.utils import normalize_type, unify_types
from lmn.compiler.typechecker.expression_checker import check_expression

# logger
logger = logging.getLogger(__name__)

def check_let_statement(stmt, symbol_table: Dict[str, str]) -> None:
    """Type check a let statement and update the symbol table."""
    var_name = stmt.variable.name
    type_annotation = stmt.type_annotation
    expr = stmt.expression

    logger.debug(f"Processing let statement for variable '{var_name}'")
    logger.debug(f"Type annotation: {type_annotation}")

    # Convert type annotation to internal format
    declared_type = normalize_type(type_annotation) if type_annotation else None

    if expr:
        # If there's an expression, typecheck it, passing the declared type as target
        logger.debug(f"Typechecking expression for variable '{var_name}'.")
        expr_type = check_expression(expr, symbol_table, declared_type)
        logger.debug(f"Expression type for '{var_name}' resolved to {expr_type}")

        # Verify compatibility
        if declared_type:
            # Use unify_types to check compatibility for assignment
            unified_type = unify_types(declared_type, expr_type, for_assignment=True)
            if unified_type != declared_type:
                raise TypeError(f"Cannot assign {expr_type} to variable of type {declared_type}")

        # Add to symbol table and update AST nodes
        symbol_table[var_name] = declared_type or expr_type
        stmt.inferred_type = expr_type
        stmt.variable.inferred_type = declared_type or expr_type

        logger.debug(f"Added '{var_name}' with type {declared_type or expr_type} to the symbol table.")

    else:
        # No expression - just add declared type to symbol table
        logger.debug(f"No expression provided in 'let' statement for variable '{var_name}'.")
        symbol_table[var_name] = declared_type
        stmt.variable.inferred_type = declared_type  # Add this line
        logger.debug(f"Marking '{var_name}' with type {declared_type} in the symbol table.")
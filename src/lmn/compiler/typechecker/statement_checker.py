# file: lmn/compiler/typechecker/statement_checker.py

import logging
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.statements.assignment_statement import check_assignment_statement
from lmn.compiler.typechecker.statements.let_statement import check_let_statement
from lmn.compiler.typechecker.statements.return_statement import check_return_statement
from lmn.compiler.typechecker.utils import normalize_type

logger = logging.getLogger(__name__)

def check_statement(stmt, symbol_table: dict) -> None:
    """
    A single statement could be LetStatement, PrintStatement, ReturnStatement, etc.
    We'll dispatch by stmt.type.
    """

    # Log the statement type and relevant details
    logger.debug(f"check_statement called for {stmt.type}")
    logger.debug(f"Current statement details: {stmt.__dict__}")
    logger.debug(f"Symbol table before statement: {symbol_table}")

    try:
        stype = stmt.type
        if stype == "LetStatement":
            check_let_statement(stmt, symbol_table)

        elif stype == "AssignmentStatement":
            check_assignment_statement(stmt, symbol_table)

        elif stype == "PrintStatement":
            check_print_statement(stmt, symbol_table)

        elif stype == "ReturnStatement":
            check_return_statement(stmt, symbol_table)

        elif stype == "FunctionDefinition":
            check_function_definition(stmt, symbol_table)

        else:
            raise NotImplementedError(f"Unsupported statement type: {stype}")

        # After we've successfully processed the statement, log the updated symbol table
        logger.debug("Statement processed successfully.")
        logger.debug(f"Updated symbol table: {symbol_table}")

    except TypeError as e:
        # Re-raise with context
        logger.error(f"Type error in {stype}: {e}")
        raise TypeError(
            f"Error in {stype} "
            f"(variable={getattr(stmt, 'variable_name', getattr(stmt, 'name', 'unknown'))}): {e}"
        )


def check_print_statement(print_stmt, symbol_table: dict) -> None:
    """
    e.g. print_stmt.expressions is a list of Expression
    """
    logger.debug(f"check_print_statement called for expressions: {print_stmt.expressions}")

    for expr in print_stmt.expressions:
        e_type = check_expression(expr, symbol_table)
        logger.debug(f"Expression '{expr}' resolved to type {e_type}")


def check_function_definition(func_def, symbol_table: dict) -> None:
    """
    1) Register the function's name, param types, return type in 'symbol_table'.
    2) Then type-check the function body.
    """

    logger.debug(f"check_function_definition called for function: {func_def.name}")

    func_name = func_def.name

    # Gather parameter types
    param_types = []
    for param in func_def.params:
        declared = param.type_annotation or "int"
        normalized = normalize_type(declared)
        param_types.append(normalized)

    # Grab the return type if present
    declared_return_type = getattr(func_def, "return_type", None) or "void"
    declared_return_type = normalize_type(declared_return_type)

    logger.debug(f"Registering function '{func_name}' with param_types={param_types} and return_type={declared_return_type}")

    # 1) Register the function signature
    symbol_table[func_name] = {
        "param_types": param_types,
        "return_type": declared_return_type
    }

    local_scope = dict(symbol_table)
    for i, param in enumerate(func_def.params):
        local_scope[param.name] = param_types[i]

    logger.debug(f"Local scope for '{func_name}' after adding parameters: {local_scope}")

    # 3) Check each statement in the function body
    for stmt in func_def.body:
        logger.debug(f"Type-checking statement in '{func_name}' body: {stmt.type}")
        check_statement(stmt, local_scope)

    logger.debug(f"Finished type-checking function '{func_name}'. Symbol table now: {symbol_table}")

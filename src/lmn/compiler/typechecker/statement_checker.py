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
            # function definitions
            check_function_definition(stmt, symbol_table)

        elif stype == "BlockStatement":
            # block scoping
            check_block_statement(stmt, symbol_table)

        elif stype == "IfStatement":
            # if statement
            check_if_statement(stmt, symbol_table)

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

def check_block_statement(block_stmt, symbol_table: dict) -> None:
    """
    Type-check a block statement by creating a *local copy* of the current symbol table.
    Any new variables declared in this block go into the local scope. 
    When the block ends, those new declarations are discarded.
    """
    logger.debug("Entering new block scope")

    # 1) Create a local scope so new variables won't leak back
    local_scope = dict(symbol_table)

    # 2) For each statement in the block, check it with the local scope
    for stmt in block_stmt.statements:
        check_statement(stmt, local_scope)

    # 3) After the block ends, discard local_scope changes
    logger.debug("Exiting block scope; local declarations are discarded.")
    logger.debug(f"Symbol table remains (outer scope) = {symbol_table}")

def check_if_statement(if_stmt, symbol_table: dict) -> None:
    """
    Type-checks an IfStatement node:
    - condition: Expression
    - then_body: list of statements
    - elseif_clauses: list of ElseIfClause
    - else_body: list of statements
    """
    logger.debug("typechecker: check_if_statement called")

    # 1) Check the main `if` condition
    cond_type = check_expression(if_stmt.condition, symbol_table)
    logger.debug(f"If condition inferred type: {cond_type}")

    # If your language wants the condition to be "int" or "bool"
    if cond_type not in ("int", "bool"):
        raise TypeError(f"If condition must be int/bool, got '{cond_type}'")

    # 2) Type-check each statement in the then_body
    for stmt in if_stmt.then_body:
        check_statement(stmt, symbol_table)

    # 3) If you have one or more `elseif` clauses:
    if hasattr(if_stmt, "elseif_clauses"):
        for elseif_clause in if_stmt.elseif_clauses:
            # check its condition
            elseif_cond_type = check_expression(elseif_clause.condition, symbol_table)
            if elseif_cond_type not in ("int", "bool"):
                raise TypeError(f"ElseIf condition must be int/bool, got '{elseif_cond_type}'")

            # check each statement in its body
            for stmt in elseif_clause.body:
                check_statement(stmt, symbol_table)

    # 4) If there's an else_body
    if if_stmt.else_body:
        for stmt in if_stmt.else_body:
            check_statement(stmt, symbol_table)

    # 5) Mark the entire IfStatement as having an inferred_type
    #    Typically "void" (or None) if statements produce no value
    if_stmt.inferred_type = "void"
    logger.debug("typechecker: assigned if_stmt.inferred_type = 'void'")
    logger.debug("typechecker: finished check_if_statement")


    
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

# file: lmn/compiler/typechecker/statement_checker.py

import logging
from lmn.compiler.typechecker.expression_checker import check_expression
from lmn.compiler.typechecker.statements.assignment_statement import check_assignment_statement
from lmn.compiler.typechecker.statements.let_statement import check_let_statement
from lmn.compiler.typechecker.statements.return_statement import check_return_statement
from lmn.compiler.typechecker.utils import normalize_type, unify_types

logger = logging.getLogger(__name__)

def check_statement(stmt, symbol_table: dict) -> None:
    """
    Main entry point for statement type-checking.
    """

    logger.debug(f"check_statement called for {stmt.type}")
    logger.debug(f"Statement details: {stmt.__dict__}")
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
            # We handle function definitions right here:
            check_function_definition(stmt, symbol_table)

        elif stype == "BlockStatement":
            check_block_statement(stmt, symbol_table)

        elif stype == "IfStatement":
            check_if_statement(stmt, symbol_table)

        else:
            raise NotImplementedError(f"Unsupported statement type: {stype}")

        logger.debug("Statement processed successfully.")
        logger.debug(f"Updated symbol table: {symbol_table}")

    except TypeError as e:
        logger.error(f"Type error in {stype}: {e}")
        raise TypeError(
            f"Error in {stype} "
            f"(variable={getattr(stmt, 'variable_name', getattr(stmt, 'name', 'unknown'))}): {e}"
        )


def check_print_statement(print_stmt, symbol_table: dict) -> None:
    for expr in print_stmt.expressions:
        e_type = check_expression(expr, symbol_table)
        logger.debug(f"Print expr '{expr}' resolved to type {e_type}")


def check_block_statement(block_stmt, symbol_table: dict) -> None:
    """
    Type-check a block by creating a local scope so new variables 
    won't leak out.
    """
    logger.debug("Entering new block scope")
    local_scope = dict(symbol_table)

    for stmt in block_stmt.statements:
        check_statement(stmt, local_scope)

    logger.debug("Exiting block scope. Local declarations are discarded.")
    logger.debug(f"Symbol table remains (outer scope) = {symbol_table}")


def check_if_statement(if_stmt, symbol_table: dict) -> None:
    logger.debug("typechecker: check_if_statement called")

    # 1) Condition
    cond_type = check_expression(if_stmt.condition, symbol_table)
    logger.debug(f"If condition type: {cond_type}")
    if cond_type not in ("int", "bool"):
        raise TypeError(f"If condition must be int/bool, got '{cond_type}'")

    # 2) Then body
    for stmt in if_stmt.then_body:
        check_statement(stmt, symbol_table)

    # 3) ElseIf clauses
    if hasattr(if_stmt, "elseif_clauses"):
        for elseif_clause in if_stmt.elseif_clauses:
            elseif_cond_type = check_expression(elseif_clause.condition, symbol_table)
            if elseif_cond_type not in ("int", "bool"):
                raise TypeError(f"ElseIf condition must be int/bool, got '{elseif_cond_type}'")

            for stmt in elseif_clause.body:
                check_statement(stmt, symbol_table)

    # 4) Else body
    if if_stmt.else_body:
        for stmt in if_stmt.else_body:
            check_statement(stmt, symbol_table)

    # 5) Mark the entire IfStatement as "void"
    if_stmt.inferred_type = "void"
    logger.debug("typechecker: finished check_if_statement")


def check_function_definition(func_def, symbol_table: dict):
    """
    A unified approach:
      1. Gather param metadata (names, declared types, defaults).
      2. Store them (and a preliminary return_type) in symbol_table[func_name].
      3. Create a local scope, type-check function body => unify final return type.
      4. Update symbol_table & the AST node with final return type & param types.
    """
    func_name = func_def.name

    # --------------------------------------------------------------------
    # 1) Gather parameters
    # --------------------------------------------------------------------
    param_names = []
    param_types = []
    param_defaults = []

    for param in func_def.params:
        param_names.append(param.name)

        declared_type = getattr(param, "type_annotation", None) or "int"
        declared_type = normalize_type(declared_type)
        param_types.append(declared_type)

        if hasattr(param, "default_value"):
            param_defaults.append(param.default_value)
        else:
            param_defaults.append(None)

    # 2) Preliminary return type (could be overridden by final unification)
    declared_return_type = getattr(func_def, "return_type", None) or "void"
    declared_return_type = normalize_type(declared_return_type)

    # --------------------------------------------------------------------
    # 3) Store an initial function signature in the symbol table
    # --------------------------------------------------------------------
    symbol_table[func_name] = {
        "param_names":    param_names,
        "param_types":    param_types[:],   # make a copy if you like
        "param_defaults": param_defaults,
        "return_type":    declared_return_type
    }

    # --------------------------------------------------------------------
    # 4) Create a local scope and add parameters
    # --------------------------------------------------------------------
    local_scope = dict(symbol_table)
    local_scope["__current_function_return_type__"] = declared_return_type

    for i, p_name in enumerate(param_names):
        local_scope[p_name] = param_types[i]

    # --------------------------------------------------------------------
    # 5) Type-check the function body. ReturnStatements unify the final return type.
    # --------------------------------------------------------------------
    for stmt in func_def.body:
        check_statement(stmt, local_scope)

    # --------------------------------------------------------------------
    # 6) Finalize the function's return type
    # --------------------------------------------------------------------
    final_return_type = local_scope.get("__current_function_return_type__")
    if final_return_type is None:
        final_return_type = "void"

    # Store the unified return type back into the symbol table
    fn_info = symbol_table[func_name]
    fn_info["return_type"] = final_return_type
    symbol_table[func_name] = fn_info

    # Also update the function-def node
    func_def.return_type = final_return_type

    # --------------------------------------------------------------------
    # 7) Persist any updated param types back into the AST
    #    (in case unify_params_from_calls or body checks changed them)
    # --------------------------------------------------------------------
    # If you do any inference that modifies param_types[i], you can
    # reflect that here. If not, no big deal.
    for i, param in enumerate(func_def.params):
        param.type_annotation = param_types[i]

    logger.debug(f"Finished type-checking function '{func_name}' "
                 f"-> return_type={final_return_type}, param_types={param_types}")


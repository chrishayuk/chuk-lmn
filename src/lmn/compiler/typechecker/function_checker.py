# file: lmn/compiler/typechecker/function_checker.py
from lmn.compiler.typechecker.statement_checker import check_statement

def check_function_definition(func_def, symbol_table: dict) -> None:
    """
    If a function def has .name, .params, .body, etc.,
    we create a local symbol table for it and check each statement.
    """
    local_symbols = {}
    # If you have parameters, record them in local_symbols
    # e.g.: for param in func_def.params: local_symbols[param.name] = param.type

    for stmt in func_def.body:
        check_statement(stmt, local_symbols)

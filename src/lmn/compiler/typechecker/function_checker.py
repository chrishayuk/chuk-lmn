# function_checker.py
from .statement_checker import check_statement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition

def check_function_definition(func_def_dict: dict, symbol_table: dict) -> None:
    func_def = FunctionDefinition.model_validate(func_def_dict)

    local_symbols = {}
    for param in func_def.params:
        local_symbols[param["name"]] = param.get("type")
    
    for stmt in func_def.body:
        check_statement(stmt, local_symbols)

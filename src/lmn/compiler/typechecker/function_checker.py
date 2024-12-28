# function_checker.py
from .statement_checker import check_statement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition

def check_function_definition(func_def_dict: dict, symbol_table: dict) -> None:
    # Validate the function definition via Pydantic
    func_def = FunctionDefinition.model_validate(func_def_dict)

    # local symbol table for function
    local_symbols = {}

    # Each param is a FunctionParameter object
    for param in func_def.params:
        # param.name => the parameter name
        # param.type_annotation => the declared type or None
        local_symbols[param.name] = param.type_annotation

    # Then check the body statements in local scope
    for stmt in func_def.body:
        check_statement(stmt, local_symbols)


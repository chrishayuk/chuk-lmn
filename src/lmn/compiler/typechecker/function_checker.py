# file: lmn/compiler/typechecker/function_checker.py

import logging
from .statement_checker import check_statement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition

logger = logging.getLogger(__name__)

def check_function_definition(func_def, symbol_table: dict):
    func_name = func_def.name

    # --------------------------------------------------------------------
    # 1) Load any already-inferred function signature from the symbol table
    #    (populated in PASS 1 + unify_params_from_calls).
    # --------------------------------------------------------------------
    fn_info = symbol_table.get(func_name, {})
    inferred_param_types = fn_info.get("param_types", [])
    declared_return_type = fn_info.get("return_type", None)

    # --------------------------------------------------------------------
    # 2) Synchronize with the AST parameters:
    #    - If we already have a known type for param i in `inferred_param_types[i]`, keep it.
    #    - Else, fall back to the param.type_annotation (in case user declared it).
    # --------------------------------------------------------------------
    # Make sure param_types array is at least as long as the param list
    while len(inferred_param_types) < len(func_def.params):
        inferred_param_types.append(None)

    for i, param in enumerate(func_def.params):
        if inferred_param_types[i] is None and param.type_annotation is not None:
            inferred_param_types[i] = param.type_annotation

    # Re-store the function signature in the symbol table
    symbol_table[func_name] = {
        "param_types": inferred_param_types,
        "return_type": declared_return_type
    }

    # --------------------------------------------------------------------
    # 3) Create a local scope for type checking the function body.
    #    - We want local copies so changes don't leak out unexpectedly.
    # --------------------------------------------------------------------
    local_scope = dict(symbol_table)
    local_scope["__current_function_return_type__"] = declared_return_type

    # Each param name => the known or inferred type
    for i, param in enumerate(func_def.params):
        local_scope[param.name] = inferred_param_types[i]

    # --------------------------------------------------------------------
    # 4) Type-check each statement in the function body
    #    This will unify the return type if we see e.g. ReturnStatement
    # --------------------------------------------------------------------
    for stmt in func_def.body:
        check_statement(stmt, local_scope)

    # --------------------------------------------------------------------
    # 5) Finalize the function return type
    # --------------------------------------------------------------------
    final_return_type = local_scope.get("__current_function_return_type__")
    if final_return_type is None:
        final_return_type = "void"

    symbol_table[func_name]["return_type"] = final_return_type
    func_def.return_type = final_return_type

    # --------------------------------------------------------------------
    # 6) Persist any updated param types back into the function AST
    # --------------------------------------------------------------------
    for i, param in enumerate(func_def.params):
        param.type_annotation = inferred_param_types[i]

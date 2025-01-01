# file: lmn/compiler/typechecker/function_checker.py

import logging
from .statement_checker import check_statement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition

logger = logging.getLogger(__name__)

def check_function_definition(func_def, symbol_table: dict):
    """
    1) Insert 'func_def.name' into the global symbol_table with param/return info.
    2) Create a local scope to type-check the function body.
    3) Potentially infer or finalize the function's return type from the body.
    4) Write final types back to the AST node, ensuring code emitters see no 'None'.
    """

    func_name = func_def.name
    logger.debug(f"Registering function '{func_name}' in symbol_table")

    # Gather parameter types (default to "int" if param.type_annotation is missing).
    param_types = []
    for param in func_def.params:
        declared = param.type_annotation or "int"
        param_types.append(declared)

    # If the AST has no explicit return_type, we keep None => possible inference
    declared_return_type = getattr(func_def, "return_type", None)
    logger.debug(
        f"Declared/initial return type for '{func_name}': {declared_return_type}"
    )

    # Step 1) Record the function signature in the global symbol table
    symbol_table[func_name] = {
        "param_types": param_types,
        "return_type": declared_return_type,  # can be None => for inference
    }

    # Step 2) Create a local scope for the function body
    local_scope = dict(symbol_table)

    # Store the current function's return type for the ReturnStatement checks
    local_scope["__current_function_return_type__"] = declared_return_type

    # Insert param names => param types into local scope
    for i, param in enumerate(func_def.params):
        local_scope[param.name] = param_types[i]

    # Step 3) Type-check each statement in the function body
    for stmt in func_def.body:
        logger.debug(f"Type-checking statement in '{func_name}' body: {stmt.type}")
        check_statement(stmt, local_scope)

    # Step 4) Retrieve the possibly updated return type
    final_return_type = local_scope.get("__current_function_return_type__", None)

    # If still None => default to "void"
    if final_return_type is None:
        final_return_type = "void"
        logger.debug(
            f"No return statements found; defaulting function '{func_name}' to 'void'."
        )

    # Update the global symbol table with the final inferred/confirmed return type
    symbol_table[func_name]["return_type"] = final_return_type

    # Step 5) **Write the final types back into the AST** 
    #  (so the emitter won't see None)
    for i, param in enumerate(func_def.params):
        # param_types[i] might be "int", "float", etc.
        param.type_annotation = param_types[i]

    # If your function node uses an attribute (like .return_type),
    # store final_return_type there
    setattr(func_def, "return_type", final_return_type)

    logger.debug(
        f"Finished checking function '{func_name}'. "
        f"Final return type: {final_return_type}. "
        f"Global table is now: {symbol_table}"
    )

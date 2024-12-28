# file: lmn/compiler/typechecker/function_checker.py
import logging
from .statement_checker import check_statement
from lmn.compiler.ast.statements.function_definition import FunctionDefinition

# Configure logging
logger = logging.getLogger(__name__)

def check_function_definition(func_def, symbol_table: dict):
    """
    Insert 'func_def.name' into the global symbol_table.
    Then create a local scope to type-check the function body.
    """

    func_name = func_def.name
    logger.debug(f"Registering function '{func_name}' in symbol_table")

    # Suppose your function has param_types or you parse them here:
    param_types = []
    for param in func_def.params:
        declared = param.type_annotation or "int"
        # convert "int" -> "i32", for example
        param_types.append(declared)  

    # Example: read func_def.return_type or default to "void"
    declared_return_type = getattr(func_def, "return_type", None) or "void"

    # 1) Record the function definition in THE global symbol table:
    symbol_table[func_name] = {
        "param_types": param_types,
        "return_type": declared_return_type
    }

    # 2) Create a local scope for body statements
    local_scope = dict(symbol_table)

    # Insert param names => param types
    for i, param in enumerate(func_def.params):
        local_scope[param.name] = param_types[i]

    # 3) Type-check each statement in the function body
    for stmt in func_def.body:
        logger.debug(f"Type-checking statement in '{func_name}' body: {stmt.type}")
        check_statement(stmt, local_scope)

    logger.debug(f"Finished checking function '{func_name}'. Global table is now: {symbol_table}")



import logging
import traceback
from typing import Dict, Any

# 1) Import the built-in definitions
from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.finalize_arguments_pass import finalize_function_calls
from lmn.compiler.typechecker.statement_checker import check_statement, check_function_definition
from lmn.compiler.typechecker.builtins import BUILTIN_FUNCTIONS
from lmn.compiler.typechecker.utils import unify_types
from lmn.compiler.typechecker.expressions.expression_dispatcher import ExpressionDispatcher

logger = logging.getLogger(__name__)

class TypeCheckError(Exception):
    """Custom exception for type checking errors with detailed information."""
    def __init__(self, message: str, node_type: str = None, details: dict = None):
        self.message = message
        self.node_type = node_type
        self.details = details or {}
        super().__init__(self.message)

def log_symbol_table(symbol_table: Dict[str, Any]) -> None:
    logger.debug("Current symbol table state:")
    for var_name, var_type in symbol_table.items():
        logger.debug(f"  {var_name}: {var_type}")

def type_check_program(program_node: Program) -> None:
    """
    A multi-step approach:
      1) Gather function definitions into the symbol table, store them in a list
      2) Partially unify param types from calls (FnExpressions)
      3) Re-check each stored FunctionDefinition body (now that param types are known)
      4) Finally, check other top-level statements
    """
    logger.info("Starting type checking for program")
    
    # ---------------------------------------------------------------
    # 1) Initialize symbol table with built-ins
    # ---------------------------------------------------------------
    symbol_table: Dict[str, Any] = {}
    for fn_name, fn_sig in BUILTIN_FUNCTIONS.items():
        symbol_table[fn_name] = fn_sig

    # ---------------------------------------------------------------
    # 1a) [FIX] Convert required_params/optional_params => param_names/param_defaults
    #     for each built-in function so finalize_function_calls can reorder arguments properly.
    # ---------------------------------------------------------------
    for fn_name, fn_info in symbol_table.items():
        required_params = fn_info.get("required_params", {})
        optional_params = fn_info.get("optional_params", {})

        if not required_params and not optional_params:
            continue

        param_names = list(required_params.keys()) + list(optional_params.keys())
        param_defaults = [None] * len(required_params) + [None] * len(optional_params)

        fn_info["param_names"] = param_names
        fn_info["param_defaults"] = param_defaults

        symbol_table[fn_name] = fn_info

    try:
        function_nodes = []
        dispatcher = ExpressionDispatcher(symbol_table)

        logger.debug("=== PASS 1: Gather function definitions & unify call param types ===")
        for node in program_node.body:
            if node.type == "FunctionDefinition":
                param_types = []
                for p in node.params:
                    declared = getattr(p, "type_annotation", None)
                    param_types.append(declared)

                rt = getattr(node, "return_type", None)

                symbol_table[node.name] = {
                    "param_types": param_types,
                    "return_type": rt
                }
                function_nodes.append(node)

        unify_params_from_calls(program_node, symbol_table, dispatcher)

        logger.debug("=== PASS 2: Re-check each stored function body ===")
        for fn_node in function_nodes:
            logger.debug(f"Re-checking function: {fn_node.name}")
            check_function_definition(fn_node, symbol_table, dispatcher)
            log_symbol_table(symbol_table)

        logger.debug("=== PASS 3: Check other top-level statements ===")
        for node in program_node.body:
            if node.type != "FunctionDefinition":
                check_statement(node, symbol_table, dispatcher)
                log_symbol_table(symbol_table)

        logger.debug("=== PASS 4: Finalizing named arguments => positional ===")
        finalize_function_calls(program_node, symbol_table)

        logger.info("Type checking completed successfully")

    except TypeCheckError as e:
        logger.error(f"Type checking failed: {e.message}")
        if e.details:
            logger.error(f"Error details: {e.details}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error during type checking: {str(e)}")
        logger.critical(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        raise


# -------------------------------------------------------------------
# unify_params_from_calls
# -------------------------------------------------------------------
def unify_params_from_calls(program_node: Program, symbol_table: dict, dispatcher: ExpressionDispatcher) -> None:
    """
    Recursively find FnExpression calls in the AST,
    unify param types if unknown.
    """
    for node in program_node.body:
        unify_calls_in_node(node, symbol_table, dispatcher)

def unify_calls_in_node(node: Node, symbol_table: dict, dispatcher: ExpressionDispatcher) -> None:
    node_type = node.type

    if node_type == "FnExpression":
        fn_name = node.name.name
        fn_info = symbol_table.get(fn_name)

        if fn_info and "param_types" in fn_info:
            param_types = fn_info["param_types"]

            purely_positional = all(a.type != "AssignmentExpression" for a in node.arguments)

            if purely_positional and len(node.arguments) == len(param_types):
                for i, arg_expr in enumerate(node.arguments):
                    arg_type = partial_check_expression(arg_expr, symbol_table, dispatcher)
                    if param_types[i] is None:
                        param_types[i] = arg_type
                    else:
                        unified = unify_types(param_types[i], arg_type, for_assignment=True)
                        param_types[i] = unified

                fn_info["param_types"] = param_types

    if hasattr(node, "body") and isinstance(node.body, list):
        for subnode in node.body:
            unify_calls_in_node(subnode, symbol_table, dispatcher)

    if hasattr(node, "expressions") and isinstance(node.expressions, list):
        for expr in node.expressions:
            unify_calls_in_node(expr, symbol_table, dispatcher)

    if hasattr(node, "expression") and node.expression is not None:
        unify_calls_in_node(node.expression, symbol_table, dispatcher)

    if hasattr(node, "arguments") and isinstance(node.arguments, list):
        for arg in node.arguments:
            unify_calls_in_node(arg, symbol_table, dispatcher)


def partial_check_expression(expr: Node, symbol_table: dict, dispatcher: ExpressionDispatcher) -> str:
    """
    Minimal pass-1 expression check to infer arguments for param unification.
    """
    if expr.type == "LiteralExpression":
        lit_type = getattr(expr, "literal_type", "")
        if lit_type == "string":
            return "string"
        return "int"
    elif expr.type == "VariableExpression":
        return symbol_table.get(expr.name, "int")
    elif expr.type == "FnExpression":
        return "void"
    return "int"

# file: lmn/compiler/typechecker/function_call_type_unifier.py
import logging
from typing import Dict, Any

from lmn.compiler.ast.program import Program
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.utils import unify_types
from lmn.compiler.typechecker.expressions.expression_dispatcher import ExpressionDispatcher

logger = logging.getLogger(__name__)

def unify_params_from_calls(
    program_node: Program,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Recursively find FnExpression calls in the AST,
    unify param types if unknown.
    """
    # loop through each node in the program
    for node in program_node.body:
        # unify calls in the node
        _unify_calls_in_node(node, symbol_table, dispatcher)

def _unify_calls_in_node(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    # Get the type of the current node
    node_type = node.type

    # Check if the current node is a FnExpression
    if node_type == "FnExpression":
        # Get the function name
        fn_name = node.name.name

        # Get the function info from the symbol table
        fn_info = symbol_table.get(fn_name)

        # Check if the function exists in the symbol table
        if fn_info and "param_types" in fn_info:
            # Unify the function call types
            _unify_fn_call_types(node, fn_info, symbol_table, dispatcher)

    # Recurse into subnodes
    for attr_name in ["body", "expressions", "arguments"]:
        # Get the subnodes
        subnodes = getattr(node, attr_name, None)

        # Check if the subnodes are a list
        if isinstance(subnodes, list):
            # Iterate over the subnodes
            for sn in subnodes:
                # Recurse into the subnode
                _unify_calls_in_node(sn, symbol_table, dispatcher)

    # Single 'expression' attribute
    if hasattr(node, "expression") and node.expression is not None:
        _unify_calls_in_node(node.expression, symbol_table, dispatcher)

def _unify_fn_call_types(
    node: Node,
    fn_info: Dict[str, Any],
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    # Get the parameter types
    param_types = fn_info["param_types"]

    # Check if the arguments are purely positional
    purely_positional = all(a.type != "AssignmentExpression" for a in node.arguments)

    # If the arguments are purely positional and there is a match in length
    if purely_positional and len(node.arguments) == len(param_types):
        # Unify the types of each argument with its corresponding parameter type
        for i, arg_expr in enumerate(node.arguments):
            # perform a partial typecheck of the argument
            arg_type = _partial_check_expression(arg_expr, symbol_table, dispatcher)

            # Unify the argument type with the parameter type
            if param_types[i] is None:
                param_types[i] = arg_type
            else:
                param_types[i] = unify_types(param_types[i], arg_type, for_assignment=True)

        # Update the function information with the unified parameter types
        fn_info["param_types"] = param_types
        logger.debug(f"Unified param types for function '{node.name.name}': {param_types}")

def _partial_check_expression(
    expr: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> str:
    """
    Minimal pass-1 expression check to infer arguments for param unification.
    """
    if expr.type == "LiteralExpression":
        return getattr(expr, "literal_type", "int") or "int"
    elif expr.type == "VariableExpression":
        return symbol_table.get(expr.name, "int")
    elif expr.type == "FnExpression":
        return "void"
    return "int"

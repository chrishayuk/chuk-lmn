# file: lmn/compiler/typechecker/function_call_type_unifier.py
import logging
from typing import Dict, Any, Union, List

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
    for node in program_node.body:
        _unify_calls_in_node(node, symbol_table, dispatcher)

def _unify_calls_in_node(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Recursively walks the AST to find FnExpressions and unify param types.
    Skips statement nodes (which often don't have `node.type`) but recurses
    into their expression children (if any) so we don't miss function calls
    that appear within statements.
    """

    # 1) If node is None, just return
    if node is None:
        return

    # 2) If node has no 'type' attribute (likely a statement), skip direct checks
    #    but still recurse into possible expression-containing attributes.
    if not hasattr(node, "type"):
        # For example, many statements have .expression, .expressions, or .body
        _recurse_subnodes(node, symbol_table, dispatcher)
        return

    # 3) Safely read the node type now
    node_type = node.type

    # 4) Check if it's a FnExpression => unify param types
    if node_type == "FnExpression":
        fn_name = node.name.name  # e.g. "add" or "subtract"
        fn_info = symbol_table.get(fn_name)
        if fn_info and "param_types" in fn_info:
            _unify_fn_call_types(node, fn_info, symbol_table, dispatcher)

    # 5) Recurse into subnodes
    _recurse_subnodes(node, symbol_table, dispatcher)


def _recurse_subnodes(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Helper to handle lists or single-node attributes that might contain expressions
    (e.g. node.body, node.expressions, node.arguments, node.expression, etc.).
    """
    for attr_name in ["body", "expressions", "arguments"]:
        subnodes = getattr(node, attr_name, None)
        if isinstance(subnodes, list):
            for sn in subnodes:
                _unify_calls_in_node(sn, symbol_table, dispatcher)
        elif subnodes is not None:
            # Single node
            _unify_calls_in_node(subnodes, symbol_table, dispatcher)

    # Some nodes also have a single 'expression' attribute
    # (e.g. ReturnStatement might have `node.expression`).
    if hasattr(node, "expression"):
        subnode = node.expression
        if subnode is not None:
            _unify_calls_in_node(subnode, symbol_table, dispatcher)


def _unify_fn_call_types(
    node: Node,
    fn_info: Dict[str, Any],
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Unify the argument types in a FnExpression call with the known parameter types
    from the symbol table.
    """
    param_types = fn_info["param_types"]

    # Check if the arguments are purely positional
    purely_positional = all(a.type != "AssignmentExpression" for a in node.arguments)

    # If purely positional and length matches param_types, unify them
    if purely_positional and len(node.arguments) == len(param_types):
        for i, arg_expr in enumerate(node.arguments):
            arg_type = _partial_check_expression(arg_expr, symbol_table, dispatcher)
            if param_types[i] is None:
                param_types[i] = arg_type
            else:
                param_types[i] = unify_types(param_types[i], arg_type, for_assignment=True)

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
        # e.g. string/int/float. For simplicity, default to `int` if not known
        return getattr(expr, "literal_type", "int") or "int"
    elif expr.type == "VariableExpression":
        return symbol_table.get(expr.name, "int")
    elif expr.type == "FnExpression":
        # We can’t fully know until we see the function body, treat as "void"
        return "void"
    return "int"

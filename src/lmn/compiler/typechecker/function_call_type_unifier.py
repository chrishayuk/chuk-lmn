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
    unify param types if unknown or None, AND
    set the call's inferred_type to the function's return_type.
    """
    logger.debug("=== unify_params_from_calls: scanning top-level program body ===")

    # Walk every top-level node in the Program’s body
    for node in getattr(program_node, "body", []):
        _unify_calls_in_node(node, symbol_table, dispatcher)


def _unify_calls_in_node(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Recursively walks the AST to find FnExpressions and unify param types.
    Also sets node.inferred_type to the function return_type if we find it.
    """
    if node is None:
        return

    # If node has no "type", it's probably a container or statement node
    if not hasattr(node, "type"):
        _recurse_subnodes(node, symbol_table, dispatcher)
        return

    node_type = node.type

    if node_type == "FnExpression":
        fn_name = getattr(node.name, "name", None)
        logger.debug(f"[FnExpression] Found call to '{fn_name}'")

        fn_info = symbol_table.get(fn_name)
        if fn_info and "param_types" in fn_info:
            logger.debug(
                f"[FnExpression] Unifying call param_types for fn='{fn_name}' "
                f"with existing {fn_info['param_types']}"
            )
            _unify_fn_call_types(node, fn_info, symbol_table, dispatcher)
        else:
            logger.debug(
                f"[FnExpression] No param_types in symbol_table for fn='{fn_name}', "
                f"or fn not found => skipping unify."
            )

    # Recurse deeper
    _recurse_subnodes(node, symbol_table, dispatcher)


def _recurse_subnodes(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    A helper that looks for typical subfields: .body, .expressions, .arguments, .expression
    and calls _unify_calls_in_node on each child.
    """
    for attr_name in ("body", "expressions", "arguments"):
        subnodes = getattr(node, attr_name, None)
        if isinstance(subnodes, list):
            for sn in subnodes:
                _unify_calls_in_node(sn, symbol_table, dispatcher)
        elif subnodes is not None:
            _unify_calls_in_node(subnodes, symbol_table, dispatcher)

    # Also handle .expression if present
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
    If the function call is purely positional with matching number of arguments,
    unify each argument's type with param_types[i]. Then set node.inferred_type
    to the function's return_type from fn_info.
    """
    param_names = fn_info.get("param_names", [])
    param_types = fn_info.get("param_types", [])
    declared_return = fn_info.get("return_type", "void")

    arguments = getattr(node, "arguments", [])
    purely_positional = all(a.type != "AssignmentExpression" for a in arguments)

    logger.debug(f"[FnCall] {node.name.name} => param_types(before)={param_types}")

    # 1) If param count matches, unify or adopt each arg
    if purely_positional and len(arguments) == len(param_types):
        for i, arg_expr in enumerate(arguments):
            arg_type = _partial_check_expression(arg_expr, symbol_table, dispatcher)
            logger.debug(
                f"[FnCall unify] Param '{param_names[i] if i < len(param_names) else i}' "
                f"=> old='{param_types[i]}', arg='{arg_type}'"
            )

            if param_types[i] is None:
                param_types[i] = arg_type
            else:
                new_type = unify_types(param_types[i], arg_type, for_assignment=True)
                param_types[i] = new_type

        fn_info["param_types"] = param_types
        logger.debug(f"[FnCall unify] final param_types => {param_types}")
    else:
        logger.debug(
            f"[FnCall unify] skipping param unify => purely_positional={purely_positional}, "
            f"arg_count={len(arguments)}, param_count={len(param_types)}"
        )

    # 2) Set the call node’s inferred_type from the function's return_type
    logger.debug(
        f"[FnCall unify] Setting node.inferred_type from '{node.inferred_type}' to '{declared_return}'"
    )
    node.inferred_type = declared_return


def _partial_check_expression(
    expr: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> str:
    """
    Minimal "pass-1" expression check to guess the type of arguments for param unification.
    If we cannot figure it out, return None.
    """
    expr_type = getattr(expr, "type", None)
    if expr_type == "LiteralExpression":
        lit_type = getattr(expr, "literal_type", None)
        return lit_type or None

    elif expr_type == "VariableExpression":
        var_name = getattr(expr, "name", None)
        var_type_info = symbol_table.get(var_name, None)

        if isinstance(var_type_info, dict):
            # Possibly a closure or function
            if var_type_info.get("is_function") or var_type_info.get("is_closure"):
                logger.debug(
                    f"[_partial_check_expression] Var '{var_name}' => function => 'function'"
                )
                return "function"
            return None

        elif isinstance(var_type_info, str):
            logger.debug(
                f"[_partial_check_expression] Var '{var_name}' => type='{var_type_info}'"
            )
            return var_type_info

        logger.debug(
            f"[_partial_check_expression] Var '{var_name}' => no known type => None"
        )
        return None

    elif expr_type == "FnExpression":
        logger.debug("[_partial_check_expression] FnExpression => 'function'")
        return "function"

    elif expr_type == "BinaryExpression":
        left_type = _partial_check_expression(expr.left, symbol_table, dispatcher)
        right_type = _partial_check_expression(expr.right, symbol_table, dispatcher)
        logger.debug(
            f"[_partial_check_expression] Binary => left={left_type}, right={right_type}"
        )
        if left_type and right_type == left_type:
            return left_type
        return None

    # fallback => None
    logger.debug(
        f"[_partial_check_expression] Expression type='{expr_type}' => returning None"
    )
    return None

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
    unify param types if unknown or None.
    """
    logger.debug("=== unify_params_from_calls: scanning top-level program body ===")
    for node in getattr(program_node, "body", []):
        _unify_calls_in_node(node, symbol_table, dispatcher)

def _unify_calls_in_node(
    node: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> None:
    """
    Recursively walks the AST to find FnExpressions and unify param types.
    Skips statement nodes (which often don't have `node.type`) but recurses
    into their expression children (if any).
    """
    if node is None:
        return

    if not hasattr(node, "type"):
        # Possibly a statement node; let's still check subnodes (body, expressions, etc.)
        _recurse_subnodes(node, symbol_table, dispatcher)
        return

    node_type = node.type

    # If it's a FnExpression => unify param types
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
                f"or fn not found in symbol_table => skipping unify."
            )

    # Always recurse into subnodes
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
            _unify_calls_in_node(subnodes, symbol_table, dispatcher)

    # Some statements or nodes have a single 'expression' field
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
    Unify the argument types in a FnExpression call with the known param types
    from the symbol table. If param_types[i] is None => adopt arg_type.
    """
    param_types = fn_info.get("param_types", [])
    param_names = fn_info.get("param_names", [])

    arguments = getattr(node, "arguments", [])
    purely_positional = all(a.type != "AssignmentExpression" for a in arguments)

    logger.debug(f"[FnCall] {node.name.name} => param_types(before)={param_types}")

    # If the function has N parameters, unify each in order
    if purely_positional and len(arguments) == len(param_types):
        for i, arg_expr in enumerate(arguments):
            arg_type = _partial_check_expression(arg_expr, symbol_table, dispatcher)

            logger.debug(
                f"[FnCall unify] Param '{param_names[i] if i < len(param_names) else i}' "
                f"before unify: {param_types[i]}, arg={arg_type}"
            )

            if param_types[i] is None:
                param_types[i] = arg_type
                logger.debug(
                    f"[FnCall unify] param_types[{i}] was None => adopting '{arg_type}'"
                )
            else:
                # unify existing type with arg_type
                new_type = unify_types(param_types[i], arg_type, for_assignment=True)
                logger.debug(
                    f"[FnCall unify] param_types[{i}] unified => old='{param_types[i]}', "
                    f"arg='{arg_type}' => new='{new_type}'"
                )
                param_types[i] = new_type

        fn_info["param_types"] = param_types
        logger.debug(f"[FnCall unify] final param_types for fn='{node.name.name}': {param_types}")
    else:
        logger.debug(
            f"[FnCall unify] Skipping unify: purely_positional={purely_positional}, "
            f"len(arguments)={len(arguments)}, len(param_types)={len(param_types)}"
        )

def _partial_check_expression(
    expr: Node,
    symbol_table: Dict[str, Any],
    dispatcher: ExpressionDispatcher
) -> str:
    """
    Minimal pass-1 expression check to infer the type of arguments for param unification.
    *No forced 'int' defaults.* If we can't figure it out => return None.
    """
    expr_type = getattr(expr, "type", None)
    if expr_type == "LiteralExpression":
        lit_type = getattr(expr, "literal_type", None)
        # If no literal_type => None
        if lit_type:
            return lit_type
        else:
            logger.debug("[_partial_check_expression] Literal with no literal_type => returning None")
            return None

    elif expr_type == "VariableExpression":
        var_name = getattr(expr, "name", None)
        # If the symbol_table has a known type for var_name
        var_type = symbol_table.get(var_name, None)
        if isinstance(var_type, dict):
            # Possibly a closure or function => treat as "function" or "string"? 
            # We'll do "function" or just None if we want to unify later.
            if var_type.get("is_function") or var_type.get("is_closure"):
                logger.debug(f"[_partial_check_expression] Var '{var_name}' => function alias => returning 'function'")
                return "function"
            # else => unknown dict => None
            return None
        elif isinstance(var_type, str):
            logger.debug(f"[_partial_check_expression] Var '{var_name}' => type='{var_type}' from symbol_table")
            return var_type
        else:
            logger.debug(f"[_partial_check_expression] Var '{var_name}' => no known type => returning None")
            return None

    elif expr_type == "FnExpression":
        # Usually unknown until we see the function body => let's do "function" or None
        logger.debug("[_partial_check_expression] FnExpression => returning 'function'")
        return "function"

    elif expr_type == "BinaryExpression":
        # Minimal approach: unify left & right => adopt that if consistent
        left_type = _partial_check_expression(expr.left, symbol_table, dispatcher)
        right_type = _partial_check_expression(expr.right, symbol_table, dispatcher)
        logger.debug(f"[_partial_check_expression] Binary => left={left_type}, right={right_type}")
        # If both match => adopt that, else None
        if left_type and right_type == left_type:
            return left_type
        else:
            return None

    # fallback => None
    logger.debug(f"[_partial_check_expression] Expression type '{expr_type}' => returning None")
    return None

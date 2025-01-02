# file: lmn/compiler/typechecker/finalize_arguments_pass.py
import logging

logger = logging.getLogger(__name__)

def finalize_function_calls(node, symbol_table: dict):
    """
    Reorder named arguments -> positional, fill defaults if missing.
    Modifies FnExpression nodes in-place so their .arguments array
    is strictly positional by the end of this pass.
    """

    if not node:
        return

    node_type = getattr(node, "type", None)
    logger.debug(f"Visiting node: {node_type}")

    # 1) Recurse into sub-nodes
    if hasattr(node, "body") and isinstance(node.body, list):
        logger.debug(f"Node {node_type} has a 'body' with {len(node.body)} children")
        for child in node.body:
            finalize_function_calls(child, symbol_table)

    if hasattr(node, "expressions") and isinstance(node.expressions, list):
        logger.debug(f"Node {node_type} has 'expressions' with {len(node.expressions)} children")
        for expr in node.expressions:
            finalize_function_calls(expr, symbol_table)

    if hasattr(node, "expression") and node.expression is not None:
        logger.debug(f"Node {node_type} has a single 'expression' child")
        finalize_function_calls(node.expression, symbol_table)

    if hasattr(node, "arguments") and isinstance(node.arguments, list):
        logger.debug(f"Node {node_type} has 'arguments' with {len(node.arguments)} children")
        # Recurse into each argument first in case of nested calls
        for arg in node.arguments:
            finalize_function_calls(arg, symbol_table)

    # 2) If it's a FunctionDefinition => handle params + body
    if node_type == "FunctionDefinition":
        if hasattr(node, "params"):
            func_name = getattr(node, "name", "unknown")
            logger.debug(f"FunctionDefinition '{func_name}' has {len(node.params)} params")
            for p in node.params:
                finalize_function_calls(p, symbol_table)
        logger.debug(f"Done finalizing FunctionDefinition '{getattr(node, 'name', 'unknown')}'")
        return

    # 3) If it's an FnExpression => reorder arguments
    if node_type == "FnExpression":
        fn_name_node = getattr(node, "name", None)
        if not fn_name_node:
            logger.debug("FnExpression has no name node; skipping reordering.")
            return

        # Check if 'name' is a typical VariableExpression node
        if getattr(fn_name_node, "type", None) == "VariableExpression":
            # e.g., node.name.name == "add"
            fn_name = getattr(fn_name_node, "name", None)
        else:
            logger.debug("FnExpression name is not a simple VariableExpression; skipping reordering.")
            return

        logger.debug(f"Reordering call to function '{fn_name}'...")
        fn_info = symbol_table.get(fn_name)
        if not fn_info:
            logger.debug(f"No fn_info found for '{fn_name}' in symbol_table. Possibly builtin/unknown. Skipping.")
            return

        param_names    = fn_info.get("param_names", [])
        param_defaults = fn_info.get("param_defaults", [])
        num_params     = len(param_names)

        logger.debug(f"Function '{fn_name}' => param_names={param_names}, param_defaults={param_defaults}")

        # Build a new array final_args
        final_args = [None] * num_params
        next_pos_index = 0

        old_args = node.arguments
        logger.debug(f"Original arguments: {len(old_args)} => {old_args}")

        for arg_node in old_args:
            # If it's an AssignmentExpression => named argument
            if getattr(arg_node, "type", None) == "AssignmentExpression":
                param_name = getattr(arg_node.left, "name", None)
                if param_name not in param_names:
                    logger.debug(f"Named argument '{param_name}' not in param_names of '{fn_name}'; skipping.")
                    continue
                idx = param_names.index(param_name)
                logger.debug(f"Placing named argument for param '{param_name}' at index {idx}")
                final_args[idx] = arg_node.right
            else:
                # It's a positional argument
                if next_pos_index < num_params:
                    logger.debug(f"Placing positional argument at index {next_pos_index}")
                    final_args[next_pos_index] = arg_node
                    next_pos_index += 1
                else:
                    logger.debug("Too many positional arguments? Skipping or ignoring...")

        # Fill defaults where needed
        for i, p_default in enumerate(param_defaults):
            if final_args[i] is None and p_default is not None:
                logger.debug(f"Filling default for param '{param_names[i]}' at index {i}")
                final_args[i] = p_default
            elif final_args[i] is None:
                logger.debug(f"No argument provided for required param '{param_names[i]}' in '{fn_name}'")

        # Replace the old array with the new purely-positional array
        node.arguments = final_args
        logger.debug(f"After reordering: {node.arguments}")

        # Also finalize each new argument (some might be FnExpressions)
        for i, arg in enumerate(node.arguments):
            if arg:
                logger.debug(f"Recursively finalizing argument {i} for function '{fn_name}'")
                finalize_function_calls(arg, symbol_table)

    # 4) If node has left/right/operand, finalize them as well
    if hasattr(node, "left") and node.left:
        logger.debug(f"Node {node_type} has 'left' child to finalize")
        finalize_function_calls(node.left, symbol_table)
    if hasattr(node, "right") and node.right:
        logger.debug(f"Node {node_type} has 'right' child to finalize")
        finalize_function_calls(node.right, symbol_table)
    if hasattr(node, "operand") and node.operand:
        logger.debug(f"Node {node_type} has 'operand' child to finalize")
        finalize_function_calls(node.operand, symbol_table)

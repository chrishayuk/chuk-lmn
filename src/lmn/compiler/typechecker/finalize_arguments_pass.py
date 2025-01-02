# file: lmn/compiler/typechecker/finalize_arguments_pass.py
import logging

# set the logger
logger = logging.getLogger(__name__)

def finalize_function_calls(node, symbol_table: dict):
    """
    Reorder named arguments -> positional, fill defaults if missing.
    Modifies FnExpression nodes in-place so their .arguments array
    is strictly positional by the end of this pass.
    """
    node_type = getattr(node, "type", None)

    # 1) Recurse into any sub-nodes: body, expressions, expression, arguments
    if hasattr(node, "body") and isinstance(node.body, list):
        for child in node.body:
            finalize_function_calls(child, symbol_table)

    if hasattr(node, "expressions") and isinstance(node.expressions, list):
        for expr in node.expressions:
            finalize_function_calls(expr, symbol_table)

    if hasattr(node, "expression") and node.expression is not None:
        finalize_function_calls(node.expression, symbol_table)

    if hasattr(node, "arguments") and isinstance(node.arguments, list):
        # We'll reorder them if this is an FnExpression, but let's also
        # finalize calls inside each argument first (in case of nested calls)
        for arg in node.arguments:
            finalize_function_calls(arg, symbol_table)

    # 2) If it's a FunctionDefinition, also handle params + body
    if node_type == "FunctionDefinition":
        if hasattr(node, "params"):
            for p in node.params:
                finalize_function_calls(p, symbol_table)
        return  # Done for this node

    # 3) If it's an FnExpression => reorder arguments
    if node_type == "FnExpression":
        fn_name_node = getattr(node, "name", None)
        if not fn_name_node:
            return  # no function name => skip

        # If the name is a simple VariableExpression
        if isinstance(fn_name_node, dict) and fn_name_node.get("type") == "VariableExpression":
            fn_name = fn_name_node.get("name")
        else:
            # Possibly a nested expression or something else
            return

        fn_info = symbol_table.get(fn_name)
        if not fn_info:
            # Could be builtin or unknown function, skip or handle differently
            return

        # For user-defined, we typically have param_names/param_defaults
        param_names    = fn_info.get("param_names", [])
        param_defaults = fn_info.get("param_defaults", [])
        num_params     = len(param_names)

        final_args = [None] * num_params
        next_pos_index = 0

        old_args = node.arguments
        for arg_node in old_args:
            if arg_node.type == "AssignmentExpression":
                # Named argument => paramName=expr
                param_name = arg_node.left.name
                if param_name not in param_names:
                    # unknown param name or builtin param
                    continue
                idx = param_names.index(param_name)
                final_args[idx] = arg_node.right
            else:
                # positional
                if next_pos_index < num_params:
                    final_args[next_pos_index] = arg_node
                    next_pos_index += 1
                else:
                    # too many args? skip or error
                    pass

        # Fill defaults where needed
        for i, p_default in enumerate(param_defaults):
            if final_args[i] is None and p_default is not None:
                final_args[i] = p_default

        # Replace the old array with the new purely-positional array
        node.arguments = final_args

        # Also finalize each new argument (in case they themselves are FnExpressions)
        for arg in node.arguments:
            if arg:
                finalize_function_calls(arg, symbol_table)

    # 4) If node has left/right/operand, finalize them as well
    if hasattr(node, "left") and node.left:
        finalize_function_calls(node.left, symbol_table)
    if hasattr(node, "right") and node.right:
        finalize_function_calls(node.right, symbol_table)
    if hasattr(node, "operand") and node.operand:
        finalize_function_calls(node.operand, symbol_table)

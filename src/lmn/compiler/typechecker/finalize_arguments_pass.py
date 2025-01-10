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
    logger.debug("finalize_function_calls: Visiting node => %r", node_type)

    # -------------------------------------------------------------------------
    # 1) Recurse into typical sub-fields: body, expressions, expression, arguments
    # -------------------------------------------------------------------------
    if hasattr(node, "body") and isinstance(node.body, list):
        logger.debug("Node %r => has a 'body' with %d children", node_type, len(node.body))
        for i, child in enumerate(node.body):
            logger.debug("Visiting body[%d] => type=%r", i, getattr(child, "type", None))
            finalize_function_calls(child, symbol_table)

    if hasattr(node, "expressions") and isinstance(node.expressions, list):
        logger.debug("Node %r => has 'expressions' with %d children", node_type, len(node.expressions))
        for i, expr in enumerate(node.expressions):
            logger.debug("Visiting expressions[%d] => type=%r", i, getattr(expr, "type", None))
            finalize_function_calls(expr, symbol_table)

    if hasattr(node, "expression") and node.expression is not None:
        logger.debug("Node %r => has single 'expression' => type=%r", node_type, getattr(node.expression, "type", None))
        finalize_function_calls(node.expression, symbol_table)

    # -------------------------------------------------------------------------
    # 1a) If it's an ArrayLiteralExpression, explicitly recurse into .elements
    # -------------------------------------------------------------------------
    if node_type == "ArrayLiteralExpression":
        elements = getattr(node, "elements", [])
        logger.debug("ArrayLiteralExpression => has %d elements", len(elements))
        for i, elem in enumerate(elements):
            logger.debug("Visiting array-literal element[%d] => type=%r", i, getattr(elem, "type", None))
            finalize_function_calls(elem, symbol_table)

    # If the node has .arguments => finalize them
    if hasattr(node, "arguments") and isinstance(node.arguments, list):
        logger.debug("Node %r => has 'arguments' with %d children", node_type, len(node.arguments))
        for i, arg in enumerate(node.arguments):
            logger.debug("Visiting arguments[%d] => type=%r", i, getattr(arg, "type", None))
            finalize_function_calls(arg, symbol_table)

    # -------------------------------------------------------------------------
    # 2) If it's a FunctionDefinition => finalize its params as well
    # -------------------------------------------------------------------------
    if node_type == "FunctionDefinition":
        func_name = getattr(node, "name", "unknown")
        logger.debug("FunctionDefinition '%s' => finalizing its params (no reordering).", func_name)

        if hasattr(node, "params"):
            logger.debug("FunctionDefinition '%s' => has %d params => finalizing them", func_name, len(node.params))
            for i, p in enumerate(node.params):
                logger.debug("Visiting param[%d] => type=%r", i, getattr(p, "type", None))
                finalize_function_calls(p, symbol_table)

        logger.debug("Done with FunctionDefinition '%s'", func_name)
        return

    # -------------------------------------------------------------------------
    # 3) If it's a ConversionExpression => finalize .source_expr
    # -------------------------------------------------------------------------
    if node_type == "ConversionExpression":
        # Often, we have a FnExpression inside .source_expr
        if hasattr(node, "source_expr") and node.source_expr:
            logger.debug("ConversionExpression => finalizing source_expr => type=%r",
                         getattr(node.source_expr, "type", None))
            finalize_function_calls(node.source_expr, symbol_table)

    # -------------------------------------------------------------------------
    # 4) If it's an FnExpression => reorder arguments, fill defaults
    # -------------------------------------------------------------------------
    if node_type == "FnExpression":
        name_node = getattr(node, "name", None)
        if not name_node:
            logger.debug("FnExpression => no 'name' found => skipping reorder")
            return

        if getattr(name_node, "type", None) == "VariableExpression":
            fn_name = getattr(name_node, "name", None)
        else:
            logger.debug("FnExpression => name is not a simple VariableExpression => skipping reorder")
            return

        logger.debug("=== Reordering call to function '%s' ===", fn_name)

        # Attempt to look up function metadata
        fn_info = symbol_table.get(fn_name)
        if not fn_info:
            logger.debug("No fn_info found for '%s' => possibly builtin => skipping reordering", fn_name)
            return

        param_names    = fn_info.get("param_names", [])
        param_defaults = fn_info.get("param_defaults", [])
        num_params     = len(param_names)

        logger.debug("FnExpression '%s': param_names=%r, param_defaults=%r", fn_name, param_names, param_defaults)
        logger.debug("Original node.arguments => %r", node.arguments)

        # Build final_args
        final_args = [None] * num_params
        next_pos_index = 0

        # Reorder named vs. positional
        for i, arg_node in enumerate(node.arguments):
            arg_type = getattr(arg_node, "type", None)
            logger.debug("Examining node.arguments[%d] => type=%r", i, arg_type)

            if arg_type == "AssignmentExpression":
                param_name = getattr(arg_node.left, "name", None)
                logger.debug("Found named arg => param_name=%r", param_name)

                if param_name not in param_names:
                    logger.debug("param_name=%r not in param_names => ignoring", param_name)
                    continue

                idx = param_names.index(param_name)
                logger.debug("Placing named argument for param '%s' at final_args[%d]", param_name, idx)
                final_args[idx] = arg_node.right
            else:
                # It's positional
                if next_pos_index < num_params:
                    logger.debug("Placing positional argument => final_args[%d] = arg_node", next_pos_index)
                    final_args[next_pos_index] = arg_node
                    next_pos_index += 1
                else:
                    logger.debug("Too many positional arguments => ignoring => %r", arg_node)

        # Fill defaults if needed
        for i, p_default in enumerate(param_defaults):
            if final_args[i] is None and p_default is not None:
                logger.debug("Filling default for param[%d] => param_name=%r => p_default=%r",
                             i, param_names[i], p_default)
                final_args[i] = p_default
            elif final_args[i] is None:
                logger.debug("No argument & no default => param_name=%r => mismatch possible", param_names[i])

        logger.debug("=> final_args => %r", final_args)
        node.arguments = final_args

        # Recurse into the final arguments
        for i, arg in enumerate(node.arguments):
            logger.debug("Now finalizing final_args[%d] => %r", i, getattr(arg, "type", None))
            if arg is not None:
                finalize_function_calls(arg, symbol_table)

    # -------------------------------------------------------------------------
    # 5) If node has left/right/operand => finalize them as well
    # -------------------------------------------------------------------------
    if hasattr(node, "left") and node.left:
        logger.debug("Node %r => finalize 'left'", node_type)
        finalize_function_calls(node.left, symbol_table)

    if hasattr(node, "right") and node.right:
        logger.debug("Node %r => finalize 'right'", node_type)
        finalize_function_calls(node.right, symbol_table)

    if hasattr(node, "operand") and node.operand:
        logger.debug("Node %r => finalize 'operand'", node_type)
        finalize_function_calls(node.operand, symbol_table)

# file: lmn/compiler/emitter/wasm/expressions/fn_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class FnExpressionEmitter:
    """
    Emits code for FnExpression nodes, e.g. calling `llm("hi")` or some other function.
    """

    def __init__(self, controller):
        """
        :param controller: The main WasmEmitter (or codegen controller) that 
                           provides methods like:
         - emit_expression(node, out_lines): 
             to recursively handle sub-expressions
         - get_emitted_function_name(name: str) -> str:
             to handle any function-name aliasing
        """
        self.controller = controller

    def emit_fn(self, node, out_lines):
        """
        Example node:
          {
            "type": "FnExpression",
            "name": { "type": "VariableExpression", "name": "factorial" },
            "arguments": [ expr1, expr2, ... ],
            "inferred_type": "i32",  # or "i32_string" etc
          }

        Steps:
          1) Gather the function name from node["name"]["name"]
          2) Use get_emitted_function_name(...) to handle aliasing
          3) Emit each argument expression => leaves results on the stack
          4) call $functionName
        """
        # 1) Retrieve raw function name
        name_node = node.get("name", {})
        raw_func_name = name_node.get("name", "unknown")  # e.g. "llm" or "sum_func"

        # 2) Possibly aliased => get real function name
        real_func_name = self.controller.get_emitted_function_name(raw_func_name)

        # 3) Normalize into valid WAT function label
        wat_func_name = self._normalize_function_name(real_func_name)

        # -- Debug logging for the function name --
        logger.debug(
            "FnExpressionEmitter: Mapping raw function '%s' -> '%s' => final label '%s'",
            raw_func_name,
            real_func_name,
            wat_func_name
        )

        # Gather arguments
        arguments = node.get("arguments", [])
        logger.debug(
            "FnExpressionEmitter: function='%s', argument_count=%d",
            raw_func_name,
            len(arguments)
        )

        # 4) Emit code for each argument => pushes them on the WASM stack
        for i, arg_expr in enumerate(arguments):
            logger.debug("FnExpressionEmitter: emitting argument[%d] => %r", i, arg_expr)
            self.controller.emit_expression(arg_expr, out_lines)

        # 5) Emit final 'call $funcName'
        logger.debug("FnExpressionEmitter: Emitting call instruction -> call %s", wat_func_name)
        out_lines.append(f"  call {wat_func_name}")

        # In case the function returns something => it stays on stack unless consumed.

    def _normalize_function_name(self, name: str) -> str:
        """
        Converts user-level function names into valid WAT function references.
        Examples:
          - "myFunction"   -> "$myFunction"
          - "$$myFunction" -> "$myFunction"
          - "$alreadyOk"   -> "$alreadyOk"
        """
        if name.startswith("$$"):
            return "$" + name[2:]
        elif not name.startswith("$"):
            return f"${name}"
        else:
            return name

import logging
logger = logging.getLogger(__name__)

class FnExpressionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_fn(self, node, out_lines):
        """
        node example:
          {
            "type": "FnExpression",
            "name": { "type": "VariableExpression", "name": "factorial" },
            "arguments": [ expr1, expr2, ... ]
          }

        Steps:
         1) Emit each argument expression => pushes them on the WASM stack.
         2) Use the controller's get_emitted_function_name(...) to handle aliasing.
         3) Normalize the function name into valid WAT format (e.g. prepend '$').
         4) Emit 'call $realFunctionName'.
        """

        # 1) Emit code for each argument expression
        for arg_expr in node["arguments"]:
            self.controller.emit_expression(arg_expr, out_lines)

        # 2) Retrieve raw function name
        raw_func_name = node["name"]["name"]  # e.g. "sum_func"

        #    Get the actual function name if it's aliased
        real_func_name = self.controller.get_emitted_function_name(raw_func_name)

        # Debug log: show old vs. new name
        logger.debug(
            f"FnExpressionEmitter: Mapping raw function '{raw_func_name}' -> '{real_func_name}'"
        )

        # 3) Normalize into valid WAT function label
        wat_func_name = self._normalize_function_name(real_func_name)

        logger.debug(
            f"FnExpressionEmitter: Emitting call instruction -> call {wat_func_name}"
        )

        # 4) Emit the final call instruction
        out_lines.append(f"  call {wat_func_name}")

    def _normalize_function_name(self, name: str) -> str:
        """
        Converts user-level function names into valid WAT function references.
        Examples:
          - "myFunction"   -> "$myFunction"
          - "$$myFunction" -> "$myFunction"
          - "$alreadyOk"   -> "$alreadyOk" (unchanged)
        """
        if name.startswith("$$"):
            return "$" + name[2:]
        elif not name.startswith("$"):
            return f"${name}"
        else:
            return name

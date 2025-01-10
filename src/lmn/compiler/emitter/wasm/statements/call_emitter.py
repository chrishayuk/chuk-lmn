import logging
logger = logging.getLogger(__name__)

class CallEmitter:
    def __init__(self, controller):
        """
        :param controller: Typically the WasmEmitter instance that orchestrates emission.
                           We assume 'controller.get_emitted_function_name(...)' is
                           available to handle function aliasing.
                           We also assume 'controller.emit_expression(expr, out_lines)' is available.
        """
        self.controller = controller

    def emit_call(self, node, out_lines):
        """
        Emitting a 'CallStatement' from the AST, which looks like:
            {
              "type": "CallStatement",
              "tool_name": "myFunction",    # the function name (string)
              "arguments": [ expr1, expr2 ],
              "discardReturn": bool
            }

        Steps:
         1) Emit each argument expression => pushes them on the WASM stack in order.
         2) Use controller.get_emitted_function_name(...) to handle alias (e.g. sum_func -> anon_0).
         3) Normalize the function name into valid WAT syntax (prepend '$').
         4) Emit 'call $functionName'.
         5) If 'discardReturn' is True, emit 'drop' to discard the function's return value.
        """

        # 1) Emit each argument expression
        args = node.get("arguments", [])
        for arg in args:
            self.controller.emit_expression(arg, out_lines)

        # 2) Retrieve the raw function name from the AST (using 'tool_name')
        #    If your AST used "name" for function calls, you can fallback:
        #       raw_func_name = node.get("tool_name") or node["name"]
        raw_func_name = node["tool_name"]

        # 3) Map the raw function name to the real function name if there's an alias
        real_func_name = self.controller.get_emitted_function_name(raw_func_name)
        logger.debug(
            f"CallEmitter: raw_func_name='{raw_func_name}' -> real_func_name='{real_func_name}'"
        )

        # 4) Ensure valid WAT function labeling
        wat_func_name = self._normalize_function_name(real_func_name)
        logger.debug(f"CallEmitter: Emitting call -> call {wat_func_name}")
        out_lines.append(f"  call {wat_func_name}")

        # 5) Optionally discard the return value
        if node.get("discardReturn", False):
            logger.debug("CallEmitter: 'discardReturn' is True, emitting 'drop'")
            out_lines.append("  drop")

    def _normalize_function_name(self, name: str) -> str:
        """
        Convert user-level names like "myFunction" to "$myFunction",
        or "$$myFunction" to "$myFunction".
        If it already starts with '$', keep it as is.
        """
        if name.startswith("$$"):
            return "$" + name[2:]
        elif not name.startswith("$"):
            return f"${name}"
        else:
            return name

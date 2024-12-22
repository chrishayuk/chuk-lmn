class CallEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_call(self, node, out_lines):
        """
        node example:
          {
            "type": "CallStatement",
            "name": "myFunction",
            "arguments": [ expr1, expr2, ... ],
            "discardReturn": true or false (optional)
              # If true, we'll 'drop' the return value
          }

        We'll:
          1. Emit each argument to push it on the WASM stack.
          2. Emit 'call $myFunction'.
          3. If the function returns a value but the language semantics say
             we don't need it, optionally emit 'drop'.
        """

        # 1) Emit each argument
        for arg in node["arguments"]:
            self.controller.emit_expression(arg, out_lines)

        # 2) Normalize the function name if your IR might have double '$'
        func_name = node["name"]
        func_name = self._normalize_function_name(func_name)

        out_lines.append(f"  call {func_name}")

        # 3) If the function returns a value but we don't need it, 'drop' it
        #    This depends on your language semantics or AST flags.
        if node.get("discardReturn", False):
            out_lines.append("  drop")

    def _normalize_function_name(self, name: str) -> str:
        """
        If you want to handle cases like 'myFunction' -> '$myFunction'
        or '$$myFunction' -> '$myFunction', use this helper.
        If you don't need it, you can remove or simplify.
        """
        if name.startswith("$$"):
            return "$" + name[2:]
        elif not name.startswith("$"):
            return f"${name}"
        return name

# compiler/emitter/wasm/statements/call_emitter.py
class CallEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_call(self, node, out_lines):
        """
        node example:
          {
            "type": "CallStatement",
            "name": "myFunction",
            "arguments": [ expr1, expr2, ... ]
          }

        We'll:
          1. Emit each argument to push it on the WASM stack,
          2. Emit 'call $myFunction'.
          3. If the function returns a value, we might want to drop it if it's not used.
        """

        # 1) Emit each argument
        for arg in node["arguments"]:
            self.controller.emit_expression(arg, out_lines)

        # 2) Call the function by name
        func_name = node["name"]
        out_lines.append(f'  call ${func_name}')

        # 3) If the function returns a value but you don't need it,
        #    you might optionally emit 'drop' here:
        #
        # out_lines.append('  drop')
        #
        # That depends on whether your function actually returns something,
        # and whether your language semantics require discarding that return value.

# compiler/emitter/wasm/expressions/variable_expression_emitter.py
class VariableExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We'll typically do something like 'local.get $var_name' or
        'global.get $var_name' depending on how variables are stored.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node structure:
          {
            "type": "VariableExpression",
            "name": "x"
          }

        We assume 'x' is a local variable for now, so we'll do 'local.get $x'.
        If it were a global, you'd use 'global.get $x' or something similar.
        """
        var_name = node["name"]

        # Emit a local.get. If your compiler uses a different scheme (globals,
        # environment lookups, etc.), adjust accordingly.
        out_lines.append(f'  local.get ${var_name}')

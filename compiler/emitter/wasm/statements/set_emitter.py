# compiler/emitter/wasm/statements/set_emitter.py
class SetEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_set(self, node, out_lines):
        """
        node example:
          {
            "type": "SetStatement",
            "variable": { "type": "VariableExpression", "name": "x" },
            "expression": <expr node>
          }

        We'll:
          1. Check if the variable name is in the local map.
             - If not, define it (i.e. emit a local declaration).
          2. Emit code for the expression (which pushes the value onto the stack).
          3. Do 'local.set $x' to store into the local variable.
        """
        var_name = node["variable"]["name"]

        # 1) If variable not in local map, define a local slot
        if var_name not in self.controller.func_local_map:
            index = self.controller.local_counter
            self.controller.func_local_map[var_name] = index
            self.controller.local_counter += 1
            out_lines.append(f'  (local $${var_name} i32)')

        # 2) Emit the expression => pushes a value onto the stack
        expr = node["expression"]
        self.controller.emit_expression(expr, out_lines)

        # 3) local.set => pops the top of the stack and stores into the local
        out_lines.append(f'  local.set $${var_name}')


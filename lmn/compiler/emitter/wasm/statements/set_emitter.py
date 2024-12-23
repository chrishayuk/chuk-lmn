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
          1. Add the variable to new_locals if it's not already known.
          2. Emit code for the expression (which pushes the value onto the stack).
          3. Emit 'local.set $x' to pop the stack and store into the local.
        """

        # 1) Extract the variable name and possibly normalize it
        var_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(var_name)  # if you have a normalization helper

        # If the variable doesn't exist in func_local_map, mark it for declaration
        if var_name not in self.controller.func_local_map:
            # For indexing locals if you need it
            index = self.controller.local_counter
            self.controller.func_local_map[var_name] = index
            self.controller.local_counter += 1

            # Add var_name to new_locals so that FunctionEmitter will emit (local $x i32)
            # in the correct position (right after the function signature).
            self.controller.new_locals.add(var_name)

        # 2) Emit the expression => pushes a value onto the stack
        expr = node["expression"]
        self.controller.emit_expression(expr, out_lines)

        # 3) local.set => pops the top of the stack and stores into the local
        out_lines.append(f'  local.set {var_name}')



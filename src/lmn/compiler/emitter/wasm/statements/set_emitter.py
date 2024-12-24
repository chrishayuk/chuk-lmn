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
          1. Add the variable to new_locals if it's not already known (inferred type).
          2. Emit code for the expression (which pushes the value onto the stack).
          3. Emit 'local.set $x' to pop the stack and store into the local.
        """

        var_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(var_name)  # If you have a normalization helper

        # The expression to assign
        expr = node["expression"]

        # 1) If the variable doesn't exist in func_local_map, infer its type & declare it
        if var_name not in self.controller.func_local_map:
            expr_type = self.controller.infer_type(expr)  # must define infer_type somewhere
            index = self.controller.local_counter
            self.controller.local_counter += 1

            # Save index + type in func_local_map. 
            # Or if you're only storing a single int for the index, 
            # you might need another structure to store the type.
            self.controller.func_local_map[var_name] = {
                "index": index,
                "type": expr_type
            }

            # Add to new_locals so FunctionEmitter can emit `(local $x i32)` or `(local $x f32)`, etc.
            self.controller.new_locals.add(var_name)

        else:
            # If we already have a known type for var_name, you might want to:
            #  - Re-infer the type from 'expr'
            #  - Check if it matches (or unify, or produce an error if they differ)
            existing_info = self.controller.func_local_map[var_name]
            existing_type = existing_info["type"]
            expr_type = self.controller.infer_type(expr)
            if expr_type != existing_type:
                # Option A: unify 
                #   new_type = unify(existing_type, expr_type)
                #   existing_info["type"] = new_type
                #   (but that might require re-declaring the local or an error)
                #
                # Option B: produce an error or warning
                # raise TypeError(f"Variable '{var_name}' was {existing_type}, now assigned {expr_type}")
                pass

        # 2) Emit the expression => pushes a value onto the stack
        self.controller.emit_expression(expr, out_lines)

        # 3) local.set => pops the top of the stack and stores it in the local
        out_lines.append(f'  local.set {var_name}')

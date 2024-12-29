# file: lmn/compiler/emitter/wasm/expressions/assignment_expression_emitter.py

class AssignmentExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is your main WasmEmitter, giving access to:
         - controller.emit_expression(...)
         - controller._normalize_local_name(...)
         - controller.func_local_map (symbol table for locals)
         etc.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example AST structure:
          {
            "type": "AssignmentExpression",
            "left":  { "type": "VariableExpression", "name": "a" },
            "right": { ...some expression... },
            "inferred_type": "i32"   # or "f64", etc.
          }

        Emission strategy (C/C++-style):
          1) Evaluate the RHS => push the result on the stack.
          2) local.set $a
          3) local.get $a   # so the expression itself yields the new value of a on the stack
        """

        # 1) Emit code for the right-hand side
        right_expr = node["right"]
        self.controller.emit_expression(right_expr, out_lines)

        # 2) local.set <var_name>
        left_var = node["left"]
        if left_var["type"] != "VariableExpression":
            # If your language allows more complex LHS, handle it. For now, assume variable only.
            raise TypeError(f"AssignmentExpression LHS must be a variable, got {left_var['type']}")

        raw_name = left_var["name"]
        normalized_name = self.controller._normalize_local_name(raw_name)
        out_lines.append(f"  local.set {normalized_name}")

        # 3) If your language wants the assignment expression itself to yield the new value
        #    (like in C, where (a = 5) can appear in further expressions),
        #    do local.get again so the final value is on stack:
        out_lines.append(f"  local.get {normalized_name}")

# file: lmn/compiler/emitter/wasm/expressions/assignment_expression_emitter.py

class AssignmentExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is your main WasmEmitter, giving access to:
         - controller.emit_expression(...)
         - controller._normalize_local_name(...)
         - controller.func_local_map (symbol table for locals)
         - controller.new_locals (set of new local variables to declare)
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
          3) local.get $a  # so the expression itself yields the new value of a on the stack
        """

        # 1) Emit code for the right-hand side (RHS)
        right_expr = node["right"]
        self.controller.emit_expression(right_expr, out_lines)

        # 2) The left side must be a variable
        left_var = node["left"]
        if left_var["type"] != "VariableExpression":
            # If your language allows more complex LHS, handle it. For now, assume variable only.
            raise TypeError(
                f"AssignmentExpression LHS must be a variable, got {left_var['type']}"
            )

        raw_name = left_var["name"]  # e.g. "a"
        if raw_name not in self.controller.func_local_map:
            # If it's truly new, mark it for declaration.
            self.controller.new_locals.add(raw_name)

        # 3) Emit local.set using the normalized name for WAT
        normalized_name = self.controller._normalize_local_name(raw_name)
        out_lines.append(f"  local.set {normalized_name}")

        # 4) If your language wants the assignment expression itself to yield
        #    the new value (like C-style '(a = 5)' used in further expressions),
        #    do local.get so the final value remains on stack:
        out_lines.append(f"  local.get {normalized_name}")

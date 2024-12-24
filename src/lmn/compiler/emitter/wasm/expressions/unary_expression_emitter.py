# compiler/emitter/wasm/expressions/unary_expression_emitter.py

class UnaryExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We rely on controller.emit_expression(...) to generate code for the operand.
        If your emitter tracks type information, you'll need to figure out the type
        of the operand so you can emit the correct WASM instruction for negation, etc.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure (example):
          {
            "type": "UnaryExpression",
            "operator": "-",         # or "+"
            "operand": { ... AST node for the operand ... }
          }

        We'll generate code for the operand, then apply the unary op:

          - operator "+" => do nothing (just emit the operand)
          - operator "-" => numeric negation:
                i32 -> (local expression) i32.const -1, i32.mul
                i64 -> (local expression) i64.const -1, i64.mul
                f32 -> f32.neg
                f64 -> f64.neg
          - operator "not" => integer eqz (i32.eqz or i64.eqz).
        """
        op = node["operator"]   # e.g. "-" or "not"
        operand = node["operand"]

        # 1) Emit the operand expression (this should push a value on the WASM stack).
        self.controller.emit_expression(operand, out_lines)

        # 2) Figure out the type of the operand.
        #    This can be done in many ways. One naive approach: call a helper that
        #    tries to infer the type from the AST node, or if your compiler already
        #    stores types in the node, you can read them directly, e.g. operand["wasmType"].
        operand_type = self._infer_operand_type(operand)

        # 3) Apply the operator based on the operand type.
        if op == "+":
            # unary plus => do nothing; the operand is already on stack
            pass

        elif op == "-":
            # numeric negation
            if operand_type == "i32":
                out_lines.append("  i32.const -1")
                out_lines.append("  i32.mul")
            elif operand_type == "i64":
                out_lines.append("  i64.const -1")
                out_lines.append("  i64.mul")
            elif operand_type == "f32":
                # f32.neg: negates the top of the stack
                out_lines.append("  f32.neg")
            elif operand_type == "f64":
                out_lines.append("  f64.neg")
            else:
                raise ValueError(f"Unsupported unary '-' for type {operand_type}")

        elif op == "not":
            # Boolean negation for integer types:
            #   i32.eqz => 0 -> 1, nonzero -> 0
            #   i64.eqz => 0 -> 1, nonzero -> 0 (support in some Wasm extensions, or do a compare)
            if operand_type == "i32":
                out_lines.append("  i32.eqz")
            elif operand_type == "i64":
                # There's no direct i64.eqz in the original Wasm MVP. 
                # In the Wasm 2.0 spec or post-MVP, i64.eqz exists.
                # If not, you can implement i64.eqz using "i64.eqz" if your toolchain supports it:
                out_lines.append("  i64.eqz")
            else:
                raise ValueError(f"Unsupported unary 'not' for type {operand_type}")

        else:
            # fallback / unknown unary operator
            raise ValueError(f"Unknown unary operator: {op}")

    def _infer_operand_type(self, operand_node):
        """
        A placeholder for type inference or retrieving stored type info.
        We do a naive approach again: if operand node is a literal, we guess type
        by presence of '.' or magnitude. If it's a variable, we might look it up
        in controller.func_local_map, etc.  This is heavily simplified.
        """

        # For demonstration, let's assume we have a helper:
        return self.controller.infer_type(operand_node)

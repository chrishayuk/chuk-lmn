# file: compiler/emitter/wasm/expressions/unary_expression_emitter.py

class UnaryExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We rely on controller.emit_expression(...) to generate code for the operand.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node:
        {
          "type": "UnaryExpression",
          "operator": "-",
          "operand": { ... AST node for the operand ... }
        }
        We'll generate code for the operand, then apply the unary op.
        """

        op = node["operator"]        # e.g. "-" or "not"
        operand = node["operand"]

        # 1) If we want to constant-fold, we can do it here BEFORE emitting:
        #    If operand is a LiteralExpression with an int value, replace
        #    the entire node with a negative literal:
        folded = self._try_constant_fold(node)
        if folded is not None:
            # folded => (wasmType, literal_value) e.g. ("i32", -1)
            # So we can directly emit i32.const -1, etc.
            self._emit_constant(folded[0], folded[1], out_lines)
            return

        # else => do normal approach

        # 2) Emit code for the operand => push it on the stack
        self.controller.emit_expression(operand, out_lines)

        # 3) Infer the operand type so we know i32 vs i64 vs f32 vs f64
        operand_type = self._infer_operand_type(operand)

        # 4) Apply the operator
        if op == "+":
            # unary plus => do nothing
            pass

        elif op == "-":
            # numeric negation (dynamic approach)
            if operand_type == "i32":
                # i32.const -1, i32.mul
                out_lines.append("  i32.const -1")
                out_lines.append("  i32.mul")
            elif operand_type == "i64":
                out_lines.append("  i64.const -1")
                out_lines.append("  i64.mul")
            elif operand_type == "f32":
                out_lines.append("  f32.neg")
            elif operand_type == "f64":
                out_lines.append("  f64.neg")
            else:
                raise ValueError(f"Unsupported unary '-' for type {operand_type}")

        elif op == "not":
            if operand_type == "i32":
                out_lines.append("  i32.eqz")
            elif operand_type == "i64":
                out_lines.append("  i64.eqz")  # if your toolchain supports i64.eqz
            else:
                raise ValueError(f"Unsupported unary 'not' for type {operand_type}")

        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def _infer_operand_type(self, operand_node):
        """
        A simplified approach: we rely on the controller.infer_type to do the actual logic
        """
        return self.controller.infer_type(operand_node)

    def _try_constant_fold(self, unary_node):
        """
        If the operand is a LiteralExpression with an integer value,
        and the operator is '-', we can fold it into a negative literal.

        Returns (wasmType, foldedValue) if successful, else None
        """
        op = unary_node["operator"]
        operand = unary_node["operand"]

        if op == "-" and operand["type"] == "LiteralExpression":
            val = operand.get("value")
            if isinstance(val, int):
                # if operand was i32 or i64 (we can check or guess from 'literal_type')
                # we'll guess i32 for smaller range, or your logic might do:
                # if operand["literal_type"] == "i64": => "i64", ...
                # We'll do i32 for demonstration:
                if operand.get("literal_type") in ("i64", "long"):
                    wasm_type = "i64"
                else:
                    wasm_type = "i32"
                return (wasm_type, -val)

        return None

    def _emit_constant(self, wasm_type, value, out_lines):
        """
        Emit e.g. i32.const <value> or i64.const <value>.
        """
        if wasm_type == "i32":
            out_lines.append(f"  i32.const {value}")
        elif wasm_type == "i64":
            out_lines.append(f"  i64.const {value}")
        else:
            raise ValueError(f"_emit_constant not implemented for {wasm_type}")

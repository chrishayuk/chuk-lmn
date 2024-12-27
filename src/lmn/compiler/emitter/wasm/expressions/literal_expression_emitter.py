# file: compiler/emitter/wasm/expressions/literal_expression_emitter.py
class LiteralExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We'll call controller.emit_expression(...) for sub-expressions if needed,
        but for a literal, we usually just generate code to push it on the WASM stack.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node structure:
          {
            "type": "LiteralExpression",
            "value": 2.718,
            "inferred_type": "f32"
          }
        """
        # 1) See if the typechecker has assigned an "inferred_type"
        inferred_t = node.get("inferred_type")
        literal_value = str(node["value"]).strip()

        if inferred_t in ("i32", "i64", "f32", "f64"):
            # Use the typechecker’s result
            if inferred_t == "i32":
                out_lines.append(f"  i32.const {literal_value}")
            elif inferred_t == "i64":
                out_lines.append(f"  i64.const {literal_value}")
            elif inferred_t == "f32":
                # Convert or strip trailing 'f' if your typechecker doesn't do it
                out_lines.append(f"  f32.const {literal_value}")
            elif inferred_t == "f64":
                out_lines.append(f"  f64.const {literal_value}")
        else:
            # 2) Fallback if no 'inferred_type' (rare if your typechecker is consistent)
            # We'll do the old 'guessing logic' if needed
            # or we can raise an error.
            num_type = self._infer_wasm_type(literal_value)
            if num_type == 'i32':
                out_lines.append(f'  i32.const {literal_value}')
            elif num_type == 'i64':
                out_lines.append(f'  i64.const {literal_value}')
            elif num_type == 'f32':
                out_lines.append(f'  f32.const {literal_value}')
            elif num_type == 'f64':
                out_lines.append(f'  f64.const {literal_value}')
            else:
                raise ValueError(f"Unsupported numeric type for literal: {literal_value}")

    def _infer_wasm_type(self, literal_str):
        """
        Naive fallback if there's no 'inferred_type'.
        """
        is_float_syntax = ('.' in literal_str) or ('e' in literal_str.lower())
        if is_float_syntax:
            # If there's a trailing 'f' or 'F', call it f32
            if literal_str.lower().endswith('f'):
                return 'f32'
            else:
                return 'f64'
        else:
            # It's integer-like
            try:
                val = int(literal_str, 0)
            except ValueError:
                return 'f64'  # fallback
            if -2147483648 <= val <= 2147483647:
                return 'i32'
            else:
                return 'i64'

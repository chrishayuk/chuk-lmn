# compiler/emitter/wasm/expressions/literal_expression_emitter.py

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
            "value": "123"
          }
          or
          {
            "type": "LiteralExpression",
            "value": "3.14"
          }
          or
          {
            "type": "LiteralExpression",
            "value": "123456789012"  (fits in i64 but not i32)
          }
        """

        literal_str = str(node["value"]).strip()
        num_type = self._infer_wasm_type(literal_str)

        if num_type == 'i32':
            out_lines.append(f'  i32.const {literal_str}')
        elif num_type == 'i64':
            out_lines.append(f'  i64.const {literal_str}')
        elif num_type == 'f32':
            # If the literal had an 'f' suffix, remove it for the actual numeric
            numeric_value = literal_str.lower().rstrip('f')
            out_lines.append(f'  f32.const {numeric_value}')
        elif num_type == 'f64':
            out_lines.append(f'  f64.const {literal_str}')
        else:
            # Fallback (should never happen if _infer_wasm_type covers all)
            raise ValueError(f"Unsupported numeric type for literal: {literal_str}")

    def _infer_wasm_type(self, literal_str):
        """
        Returns one of 'i32', 'i64', 'f32', 'f64' based on a naive analysis of the literal string.
        Some rules (you can change them as you like):
          1) If it contains '.' or 'e'/'E', consider it float/double.
          2) If it ends with 'f'/'F', call it f32. Otherwise f64.
          3) If it's purely an integer, parse it in Python. If it's in signed 32-bit range => i32, else i64.
        """

        # Quick check for float-like syntax
        is_float_syntax = ('.' in literal_str) or ('e' in literal_str.lower())

        if is_float_syntax:
            # If there's a trailing 'f' or 'F', call it f32
            if literal_str.lower().endswith('f'):
                return 'f32'
            else:
                return 'f64'
        else:
            # It's integer-like (no '.' or 'e')
            # We'll parse as int in Python
            try:
                val = int(literal_str, 0)  # base=0 handles "0x..." or "0b..." if you like
            except ValueError:
                # If we can't parse it as an int, fallback to f64
                return 'f64'

            # Check 32-bit range: -2^31 <= val < 2^31
            if -2147483648 <= val <= 2147483647:
                return 'i32'
            else:
                return 'i64'

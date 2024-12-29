# file: compiler/emitter/wasm/statements/print_emitter.py

class PrintEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_print(self, node, out_lines):
        """
        node structure example:
        {
          "type": "PrintStatement",
          "expressions": [
            {
              "type": "LiteralExpression",
              "value": 42,
              "inferred_type": "i32"
            },
            {
              "type": "LiteralExpression",
              "value": 4294967296,
              "inferred_type": "i64"
            },
            {
              "type": "LiteralExpression",
              "value": 3.14,
              "inferred_type": "f64"
            },
            {
              "type": "LiteralExpression",
              "value": "Hello world",
              "inferred_type": "string"  # or 'i32' if everything is forced to i32
            },
            ...
          ]
        }
        """

        exprs = node["expressions"]
        for ex in exprs:
            # 1) Check if it's a string literal
            if (ex["type"] == "LiteralExpression"
                and isinstance(ex["value"], str)):

                # A) Option 1: Just log a comment
                string_val = ex["value"]
                out_lines.append(f'  ;; skipping string literal: {string_val}')
                # B) Or produce a placeholder if you prefer:
                # out_lines.append('  i32.const 0  ;; placeholder for string')
                # out_lines.append('  call $print_i32')
                continue

            # 2) Otherwise treat it as numeric
            self.controller.emit_expression(ex, out_lines)

            # 3) Based on the inferred type, call the matching print function
            inferred_type = ex.get("inferred_type", "i32")  # fallback to i32 if missing

            if inferred_type == "i64":
                out_lines.append("  call $print_i64")

            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")

            elif inferred_type == "f32":
                # If you only have `print_f64` imported, promote f32 -> f64
                out_lines.append("  f64.promote_f32")
                out_lines.append("  call $print_f64")

            else:
                # default => treat as i32
                out_lines.append("  call $print_i32")

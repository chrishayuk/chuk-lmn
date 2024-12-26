# compiler/emitter/wasm/statements/print_emitter.py

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
            ...
          ]
        }
        """

        exprs = node["expressions"]
        for ex in exprs:
            # 1) If it's a string literal, handle or skip
            if ex["type"] == "LiteralExpression" and isinstance(ex["value"], str):
                # ignoring strings for simplicity
                continue

            # 2) Emit code for the numeric expression
            self.controller.emit_expression(ex, out_lines)

            # 3) Based on inferred type, call the matching print function
            inferred_type = ex.get("inferred_type", "i32")  # fallback to i32 if missing
            if inferred_type == "i64":
                out_lines.append("  call $print_i64")
            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")
            else:
                # default or i32
                out_lines.append("  call $print_i32")

# file: lmn/compiler/emitter/wasm/statements/print_emitter.py

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
              "value": "Hello world",
              "inferred_type": "string"
            },
            {
              "type": "LiteralExpression",
              "value": "[1,2,3]",
              "inferred_type": "i32_ptr"
            },
            {
              "type": "LiteralExpression",
              "value": "{'name':'Alice'}",
              "inferred_type": "i32_json"
            },
            ...
          ]
        }
        """

        exprs = node["expressions"]
        for ex in exprs:
            # 1) Emit code to push the expression's value on the stack
            self.controller.emit_expression(ex, out_lines)

            # 2) Based on the 'inferred_type', pick an appropriate print function
            inferred_type = ex.get("inferred_type", "i32")  # fallback to i32 if missing

            if inferred_type == "i64":
                out_lines.append("  call $print_i64")

            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")

            elif inferred_type == "f32":
                out_lines.append("  call $print_f32")

            elif inferred_type in ("string", "i32_ptr"):
                """
                Here we assume you have an import like:
                (import "env" "print_string" (func $print_string (param i32)))

                'string' => was a textual literal => data segment offset
                'i32_ptr' => an array pointer offset, but let's print as if it's textual or handle it differently
                """
                out_lines.append("  call $print_string")

            elif inferred_type == "i32_json":
                """
                If you want to treat JSON differently, you might have an import for printing JSON:
                (import "env" "print_json" (func $print_json (param i32)))
                """
                out_lines.append("  call $print_json")

            else:
                # default => treat as i32
                out_lines.append("  call $print_i32")

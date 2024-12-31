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
              "type": "ArrayLiteralExpression",
              "inferred_type": "i32_ptr"   # meaning it's an int[] -> pointer
            },
            {
              "type": "JsonLiteralExpression",
              "inferred_type": "i32_json"
            },
            ...
          ]
        }

        We decide how to print based on 'inferred_type':

          - i32, i64, f32, f64 => call $print_i32, $print_i64, etc.
          - string => call $print_string
          - i32_json => call $print_json
          - i32_ptr => call $print_i32_array
          - i64_ptr => call $print_i64_array
          - f32_ptr => call $print_f32_array
          - f64_ptr => call $print_f64_array

        That way, your host script can define a separate function for each typed array.
        """

        for ex in node["expressions"]:
            # 1) Emit code to push the expression's value on the stack
            self.controller.emit_expression(ex, out_lines)

            # 2) Determine which print function to call
            inferred_type = ex.get("inferred_type", "i32")  # fallback

            # ----- Numeric scalars -----
            if inferred_type == "i64":
                out_lines.append("  call $print_i64")
            elif inferred_type == "f64":
                out_lines.append("  call $print_f64")
            elif inferred_type == "f32":
                out_lines.append("  call $print_f32")
            elif inferred_type in ("i32", "int"):
                out_lines.append("  call $print_i32")

            # ----- JSON pointer -----
            elif inferred_type == "i32_json":
                out_lines.append("  call $print_json")

            # ----- Arrays (pointers in memory) -----
            elif inferred_type == "i32_ptr":
                out_lines.append("  call $print_i32_array")
            elif inferred_type == "i64_ptr":
                out_lines.append("  call $print_i64_array")
            elif inferred_type == "f32_ptr":
                out_lines.append("  call $print_f32_array")
            elif inferred_type == "f64_ptr":
                out_lines.append("  call $print_f64_array")

            # ----- Strings or textual fallback -----
            elif inferred_type == "string":
                out_lines.append("  call $print_string")

            else:
                # default => treat as i32
                out_lines.append("  call $print_i32")

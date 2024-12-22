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
              { "type": "LiteralExpression", "value": "Hello, World!" },
              { "type": "VariableExpression", "name": "x" },
              ...
            ]
          }
        """
        exprs = node["expressions"]
        for ex in exprs:
            # If it's a literal string => skip or handle separately
            if ex["type"] == "LiteralExpression" and isinstance(ex["value"], str):
                # ignoring strings for simplicity
                continue

            # Otherwise, assume it's a numeric expression
            # 1) Emit the expression => pushes an i32 on stack
            self.controller.emit_expression(ex, out_lines)

            # 2) Print using imported 'print_i32' function
            out_lines.append('  call $print_i32')

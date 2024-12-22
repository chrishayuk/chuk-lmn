# compiler/emitter/wasm/expressions/literal_expression_emitter.py
class LiteralExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We'll call controller.emit_expression(...) for sub-expressions if needed,
        but for a literal, we usually just generate a simple i32.const, etc.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node structure:
          {
            "type": "LiteralExpression",
            "value": 42
          }

        We generate code to push that literal value on the WASM stack.
        """
        value = node["value"]

        # For simplicity, assume all literals are i32 integers.
        # If your language supports floats, strings, etc.,
        # you'd branch or handle them differently.
        out_lines.append(f'  i32.const {value}')

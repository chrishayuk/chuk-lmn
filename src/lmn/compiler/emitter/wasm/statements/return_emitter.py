# file: lmn/compiler/emitter/wasm/statements/return_emitter.py

class ReturnEmitter:
    def __init__(self, controller):
        """
        The controller typically orchestrates expression emission 
        and might store additional metadata.
        """
        self.controller = controller

    def emit_return(self, node, out_lines):
        """
        node structure example:
          {
            "type": "ReturnStatement",
            // "expression": { ... expression node ... }  <--- optional
          }

        We'll emit code for the expression (if present), pushing its result
        on the stack, then emit a 'return' instruction.
        """
        # 1) Check if there's an expression
        expr = node.get("expression", None)
        if expr:
            # If present, emit expression => places the result on the stack
            self.controller.emit_expression(expr, out_lines)

        # 2) Emit the WASM 'return' instruction
        out_lines.append("  return")

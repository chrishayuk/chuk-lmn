# compiler/emitter/wasm/statements/return_emitter.py
class ReturnEmitter:
    def __init__(self, controller):
        # The 'controller' usually orchestrates the entire emission process
        self.controller = controller

    def emit_return(self, node, out_lines):
        """
        node structure example:
          {
            "type": "ReturnStatement",
            "expression": { ... expression node ... }
          }

        We'll emit code for the expression, pushing its result on the stack,
        then emit a 'return' instruction.
        """
        expr = node["expression"]
        # 1) Emit the expression => places the result on the stack
        self.controller.emit_expression(expr, out_lines)

        # 2) Emit the WASM 'return' instruction
        out_lines.append('  return')

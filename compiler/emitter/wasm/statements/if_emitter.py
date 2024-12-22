# compiler/emitter/wasm/statements/if_emitter.py
class IfEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_if(self, node, out_lines):
        """
        node: {
          "type": "IfStatement",
          "condition": <expr>,
          "thenBody": [ list of statement nodes ],
          "elseBody": [ list of statement nodes or empty ]
        }

        We'll emit something like:
          (evaluate condition -> i32 on stack)
          if
            (then
              ;; code for thenBody
            )
            (else
              ;; code for elseBody
            )
          end
        """
        cond = node["condition"]

        # 1) Evaluate the condition => pushes i32 (0 or non-0) on the WASM stack
        self.controller.emit_expression(cond, out_lines)

        # 2) Emit the WASM 'if' construct
        out_lines.append('  if')

        # 3) Then branch
        out_lines.append('    (then')
        for st in node["thenBody"]:
            self.controller.emit_statement(st, out_lines)
        out_lines.append('    )')

        # 4) Else branch (only if elseBody is not empty)
        if node["elseBody"]:
            out_lines.append('    (else')
            for st in node["elseBody"]:
                self.controller.emit_statement(st, out_lines)
            out_lines.append('    )')

        # 5) End the `if`
        out_lines.append('  end')


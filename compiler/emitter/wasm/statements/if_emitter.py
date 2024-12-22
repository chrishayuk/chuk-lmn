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

        We'll produce something like:

          ;; condition is pushed on the stack
          if
            ;; thenBody statements
          else
            ;; elseBody statements
          end

        which is valid blockless 'if' syntax in WAT.
        """

        # 1) Emit expression for condition => puts i32 (0 or non-0) on WASM stack
        cond = node["condition"]
        self.controller.emit_expression(cond, out_lines)

        # 2) Emit 'if'
        out_lines.append('  if')

        # 3) Then branch statements
        for st in node["thenBody"]:
            self.controller.emit_statement(st, out_lines)

        # 4) Else branch, only if elseBody is not empty
        if node["elseBody"]:
            out_lines.append('  else')
            for st in node["elseBody"]:
                self.controller.emit_statement(st, out_lines)

        # 5) End
        out_lines.append('  end')

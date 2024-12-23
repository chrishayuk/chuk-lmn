class IfEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_if(self, node, out_lines):
        """
        node: {
          "type": "IfStatement",
          "condition": <expr>,
          "thenBody": [ list of statement nodes ],
          "elseBody": [ list of statement nodes or empty ],
          "result": "i32" or None  (optional, if your IR specifies a return type for the if)
        }

        We'll produce something like:

          ;; condition is pushed on the stack
          if                 ;; or if (result i32)
            ;; thenBody statements
          else
            ;; elseBody statements
          end

        which is valid blockless 'if' syntax in WAT.
        """

        # 1) Emit expression for condition => puts i32 (0 or non-zero) on the WASM stack
        cond_expr = node["condition"]
        self.controller.emit_expression(cond_expr, out_lines)

        # 2) If your language or IR says this if-statement produces a value (e.g. i32),
        #    you could do something like:
        # result_type = node.get("result")
        # if result_type:
        #     out_lines.append(f'  if (result {result_type})')
        # else:
        #     out_lines.append('  if')
        #
        # For a blockless if with no result, just:
        out_lines.append('  if')

        # 3) Then-branch statements
        for statement in node["thenBody"]:
            self.controller.emit_statement(statement, out_lines)

        # 4) Else-branch, only if elseBody is not empty
        if node["elseBody"]:
            out_lines.append('  else')
            for statement in node["elseBody"]:
                self.controller.emit_statement(statement, out_lines)

        # 5) End
        out_lines.append('  end')

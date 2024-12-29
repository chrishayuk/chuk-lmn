# file: lmn/compiler/emitter/wasm/statements/if_emitter.py

class IfEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_if(self, node, out_lines):
        """
        node: {
          "type": "IfStatement",
          "condition": <expr>,
          "then_body": [ list of statements ],
          "elseif_clauses": [
            {
              "type": "ElseIfClause",
              "condition": <expr>,
              "body": [ list of statements ]
            },
            ...
          ],
          "else_body": [ list of statements ],
          ...
        }

        We'll generate nested 'if/else' blocks for chained elseifs.
        """

        # 1) Emit expression for condition => i32 on WASM stack
        self.controller.emit_expression(node["condition"], out_lines)

        # 2) Insert the 'if' instruction
        out_lines.append('  if')

        # 3) Then-branch
        then_body = node.get("then_body", [])
        for statement in then_body:
            self.controller.emit_statement(statement, out_lines)

        # 4) If there's either elseif_clauses or else_body, we do an 'else' block
        has_elseif = bool(node.get("elseif_clauses"))
        has_else   = bool(node.get("else_body"))

        if has_elseif or has_else:
            out_lines.append('  else')
            clauses = node.get("elseif_clauses", [])
            if clauses:
                # handle chain of elseifs
                self._emit_elseif_chain(clauses, node.get("else_body", []), out_lines)
            else:
                # no elseif => just else_body
                for statement in node["else_body"]:
                    self.controller.emit_statement(statement, out_lines)

        # 5) end
        out_lines.append('  end')

    def _emit_elseif_chain(self, clauses, final_else_body, out_lines):
        """
        Recursively emit a chain of ElseIfClause items as nested ifs.
        E.g. multiple elseifs become nested 'else if' in WASM by chaining:

          if (cond1)
            ...
          else
            if (cond2)
              ...
            else
              ...
            end
          end
        """

        # 1) Grab the first clause
        clause = clauses[0]

        # 2) Emit the clause condition => i32
        self.controller.emit_expression(clause["condition"], out_lines)

        out_lines.append('    if')  # Indented or not, purely aesthetic

        # 3) Then-branch => the clause.body
        for statement in clause["body"]:
            self.controller.emit_statement(statement, out_lines)

        # 4) If there's more clauses, chain them; else final_else_body
        remaining = clauses[1:]
        if remaining:
            out_lines.append('    else')
            self._emit_elseif_chain(remaining, final_else_body, out_lines)
        else:
            # final else block
            if final_else_body:
                out_lines.append('    else')
                for statement in final_else_body:
                    self.controller.emit_statement(statement, out_lines)

        # 5) end
        out_lines.append('    end')

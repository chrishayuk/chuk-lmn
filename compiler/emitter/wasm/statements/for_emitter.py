# compiler/emitter/wasm/statements/for_emitter.py

class ForEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_for(self, node, out_lines):
        """
        node = {
          "type": "ForStatement",
          "variable":  { "type": "VariableExpression", "name": "i" },
          "start_expr": <expression node>,
          "end_expr":   <expression node>,
          "step_expr":  <expression node> or None,
          "body":       [ ... statements ... ]
        }
        
        We'll compile this into WAT roughly as:
        
          (local.set $i start_expr)

          block $for_exit
            loop $for_loop
              local.get $i
              ... end_expr ...
              i32.lt_s      ;; or i32.le_s, etc.
              if
                ;; Then branch => loop body + step => br $for_loop
                ...body...
                local.get $i
                i32.const 1
                i32.add
                local.set $i
                br $for_loop
              else
                ;; do nothing, exit loop
              end
            end
          end
        """

        # 1) Extract the variable name
        var_name = node["variable"]["name"]

        # 2) Tell the controller we need a local for 'i'
        #    Instead of emitting "(local $i i32)" immediately, we rely on
        #    a function-level collector that will declare all locals upfront.
        self.controller.collect_local_declaration(var_name)

        # 3) Emit code to initialize i = start_expr
        self.controller.emit_expression(node["start_expr"], out_lines)
        out_lines.append(f'  local.set ${var_name}')

        # 4) Emit the block/loop structure
        out_lines.append('  block $for_exit')
        out_lines.append('    loop $for_loop')

        # 5) Condition check => i < end_expr (or <=, etc.)
        self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
        self.controller.emit_expression(node["end_expr"], out_lines)
        out_lines.append('  i32.lt_s')   # Adjust if you want <=, e.g. "i32.le_s"

        # 6) Use the blockless if
        out_lines.append('  if')  # Condition is on stack already

        # 6a) Then branch => loop body + step + br $for_loop
        #     Emit the statements in the body
        for st in node["body"]:
            self.controller.emit_statement(st, out_lines)

        # 6b) Handle step => i += (step_expr or 1)
        if node["step_expr"] is None:
            # default step => i += 1
            self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
            out_lines.append('  i32.const 1')
            out_lines.append('  i32.add')
            out_lines.append(f'  local.set ${var_name}')
        else:
            # i += step_expr
            self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
            self.controller.emit_expression(node["step_expr"], out_lines)
            out_lines.append('  i32.add')
            out_lines.append(f'  local.set ${var_name}')

        # Jump back to start of loop
        out_lines.append('  br $for_loop')

        # 6c) Else branch => do nothing, exit loop
        out_lines.append('  else')
        # No statements => we just allow the loop to end

        # 6d) End the if
        out_lines.append('  end')

        # 7) End the loop and block
        out_lines.append('  end')     # loop $for_loop
        out_lines.append('  end')     # block $for_exit
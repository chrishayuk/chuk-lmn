# compiler/emitter/wasm/statements/for_emitter.py
class ForEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_for(self, node, out_lines):
        """
        node = {
          "type": "ForStatement",
          "variable": { "type": "VariableExpression", "name": "i" },
          "start_expr": {...},
          "end_expr": {...},
          "step_expr": None or {...},
          "body": [ ... statements ... ]
        }
        """
        var_name = node["variable"]["name"]

        # 1) Ensure var_name is in local map
        if var_name not in self.controller.func_local_map:
            index = self.controller.local_counter
            self.controller.func_local_map[var_name] = index
            self.controller.local_counter += 1
            # Optionally declare the local (depends on your WASM text approach)
            out_lines.append(f'  (local $${var_name} i32)')

        # 2) Emit start_expr => local.set $i
        self.controller.emit_expression(node["start_expr"], out_lines)
        out_lines.append(f'  local.set $${var_name}')

        # We'll label the loop blocks
        # block => for exit
        # loop => for repeating
        out_lines.append('  block $for_exit')
        out_lines.append('    loop $for_loop')

        # 3) Condition check
        #    - push i, push end_expr, compare => if condition is true, then go to body
        self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
        self.controller.emit_expression(node["end_expr"], out_lines)

        # For simplicity, assume we want i < end_expr (strict less)
        out_lines.append('  i32.lt_s')  # or i32.le_s if your language uses <=

        # If condition is false => skip body => end of if => break
        # If condition is true  => run body => step => br $for_loop => repeat
        out_lines.append('  if')
        out_lines.append('    (then')

        # 4) Emit the loop body statements
        for st in node["body"]:
            self.controller.emit_statement(st, out_lines)

        # 5) Increment i (or use step_expr if present)
        if node["step_expr"] is None:
            # Default step => i += 1
            # push i, push 1, add => local.set $i
            self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
            out_lines.append('  i32.const 1')
            out_lines.append('  i32.add')
            out_lines.append(f'  local.set $${var_name}')
        else:
            # Evaluate "i = i + step_expr"
            self.controller.emit_expression({"type": "VariableExpression", "name": var_name}, out_lines)
            self.controller.emit_expression(node["step_expr"], out_lines)
            out_lines.append('  i32.add')
            out_lines.append(f'  local.set $${var_name}')

        # Jump back to start of loop
        out_lines.append('      br $for_loop')
        out_lines.append('    )')  # end then
        out_lines.append('  end')   # end if
        out_lines.append('  end')   # end block

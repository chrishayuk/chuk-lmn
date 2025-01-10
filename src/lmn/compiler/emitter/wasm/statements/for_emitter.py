# file: lmn/compiler/emitter/wasm/statements/for_emitter.py

class ForEmitter:
    def __init__(self, controller):
        """
        'controller' is typically a WasmEmitter instance, which provides:
          - request_local(var_name, local_type)
          - emit_expression(...)
          - emit_statement(...)
          - _normalize_local_name(...)
        """
        self.controller = controller

    def emit_for(self, node, out_lines):
        """
        node = {
          "type": "ForStatement",
          "variable":  { "type": "VariableExpression", "name": "i" },
          "start_expr": <expression node>,
          "end_expr":   <expression node> or None,
          "step_expr":  <expression node> or None,
          "body":       [ ... statements ... ]
        }

        We emit roughly:

          ;; i = start_expr
          local.set $i

          block $for_exit
            loop $for_loop
              local.get $i
              ;; push end_expr
              i32.lt_s   ;; or i32.le_s, etc.
              if
                ;; then => loop body
                ;; step => i += (step_expr or 1)
                br $for_loop
              else
                ;; exit loop
              end
            end
          end
        """

        # 1) Extract and normalize the variable name
        raw_var_name = node["variable"]["name"]
        var_name = self.controller._normalize_local_name(raw_var_name)

        # 2) Request local declaration from the emitter
        #    This used to be 'collect_local_declaration'. Now we do:
        self.controller.request_local(var_name, "i32")

        # 3) Emit code to initialize i = start_expr
        self.controller.emit_expression(node["start_expr"], out_lines)
        out_lines.append(f'  local.set {var_name}')

        # 4) Emit the block/loop structure
        out_lines.append('  block $for_exit')
        out_lines.append('    loop $for_loop')

        # 5) Condition check => i < end_expr (or <=)
        #    a) push i
        self.controller.emit_expression(
            {"type": "VariableExpression", "name": raw_var_name},
            out_lines
        )
        #    b) push end_expr
        if node["end_expr"] is not None:
            self.controller.emit_expression(node["end_expr"], out_lines)
        else:
            # In case there's no end_expr, default to something or handle an error
            out_lines.append('  i32.const 9999')  # Example default or raise an exception

        #    c) compare => i32.lt_s or i32.le_s
        out_lines.append('  i32.lt_s')   # or i32.le_s if you want i <= end_expr

        # 6) Use blockless if for the loop body
        out_lines.append('  if')  # Condition is on stack

        # 6a) Then branch => emit body statements
        for st in node["body"]:
            self.controller.emit_statement(st, out_lines)

        # 6b) Step => i += step_expr (default 1 if step_expr is None)
        self.controller.emit_expression(
            {"type": "VariableExpression", "name": raw_var_name},
            out_lines
        )
        if node["step_expr"] is None:
            out_lines.append('  i32.const 1')
        else:
            self.controller.emit_expression(node["step_expr"], out_lines)
        out_lines.append('  i32.add')
        out_lines.append(f'  local.set {var_name}')

        # 6c) Jump back to loop
        out_lines.append('  br $for_loop')

        # 6d) Else => do nothing, exit loop
        out_lines.append('  else')

        # 6e) End the if
        out_lines.append('  end')

        # 7) End loop and block
        out_lines.append('  end')  # loop $for_loop
        out_lines.append('  end')  # block $for_exit

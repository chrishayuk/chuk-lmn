# file: lmn/compiler/emitter/wasm/statements/for_emitter.py

import logging

logger = logging.getLogger(__name__)

class ForEmitter:
    def __init__(self, controller):
        """
        'controller' is typically a WasmEmitter instance, which provides:
          - request_local(var_name, local_type)
          - emit_expression(expr, out_lines)
          - emit_statement(stmt, out_lines)
          - _normalize_local_name(name)
        """
        self.controller = controller

    def emit_for(self, node, out_lines):
        """
        node = {
          "type": "ForStatement",
          "variable":  { "type": "VariableExpression", "name": "i" },
          "start_expr": <expression>,
          "end_expr":   <expression> or None,
          "step_expr":  <expression> or None,
          "body":       [ ... statements ... ]
        }

        We'll generate WAT shaped like this:

          ;; (local $i i32)  declared by request_local(...)
          ;; i = start_expr
          local.set $i

          block $for_exit
            loop $for_loop
              ;; top-of-loop condition
              local.get $i
              (end_expr or sentinel)
              i32.lt_s
              i32.eqz
              br_if $for_exit     ;; exit if !(i < end_expr)

              ;; Now a nested block for 'continue':
              block $for_continue
                ;; body statements
                ;;   if BreakStatement => br $for_exit
                ;;   if ContinueStatement => br $for_continue

                ;; normal path => fallthrough
              end $for_continue

              ;; increment step
              local.get $i
              [step_expr or i32.const 1]
              i32.add
              local.set $i

              br $for_loop
            end
          end
        """

        raw_var_name = node["variable"]["name"]
        var_name     = self.controller._normalize_local_name(raw_var_name)

        # 1) Ensure local i is declared as i32
        self.controller.request_local(var_name, "i32")

        # 2) Initialize i = start_expr
        self.controller.emit_expression(node["start_expr"], out_lines)
        out_lines.append(f"  local.set {var_name}")

        # 3) Emit the block and loop
        out_lines.append("  block $for_exit")
        out_lines.append("    loop $for_loop")

        # 4) Top-of-loop condition check
        out_lines.append(f"  local.get {var_name}")
        if node.get("end_expr") is not None:
            self.controller.emit_expression(node["end_expr"], out_lines)
        else:
            # No end_expr => pick a large sentinel
            out_lines.append("  i32.const 999999")

        # i < end_expr => i32.lt_s => if false => i >= end_expr => br_if $for_exit
        out_lines.append("  i32.lt_s")
        out_lines.append("  i32.eqz")
        out_lines.append("  br_if $for_exit")

        # 5) We open a nested block for "continue" label
        out_lines.append("  block $for_continue")

        # 6) Emit the loop body statements
        #    - If BreakStatement => br $for_exit
        #    - If ContinueStatement => br $for_continue
        #    - Otherwise => normal

        for stmt in node["body"]:
            stype = stmt["type"]

            if stype == "BreakStatement":
                out_lines.append("    br $for_exit")

            elif stype == "ContinueStatement":
                out_lines.append("    br $for_continue")

            else:
                self.controller.emit_statement(stmt, out_lines)

        # 7) End of the block for continue
        #    (if none of the statements jumped with br $for_continue,
        #     we fall through to here)
        out_lines.append("  end $for_continue")

        # 8) After the body, we do the increment step
        out_lines.append(f"  local.get {var_name}")
        step_expr = node.get("step_expr")
        if step_expr:
            self.controller.emit_expression(step_expr, out_lines)
        else:
            out_lines.append("  i32.const 1")
        out_lines.append("  i32.add")
        out_lines.append(f"  local.set {var_name}")

        # 9) Jump back to the top
        out_lines.append("  br $for_loop")

        # 10) Close the loop and the outer block
        out_lines.append("  end")  # end of loop $for_loop
        out_lines.append("  end")  # end of block $for_exit

# file: lmn/compiler/emitter/wasm/expressions/postfix_expression_emitter.py
class PostfixExpressionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node = {
          "type": "PostfixExpression",
          "operator": "++" or "--",
          "operand": { "type": "VariableExpression", "name": "a" },
          "inferred_type": "i32" (or i64/f32/f64)
        }
        We want to push the 'old value' on stack if typical C-style semantics: a++ => push old 'a',
        then a = a + 1. Or you might do 'push new value' semantics, depends on language design.
        """
        op = node["operator"]  # '++' or '--'
        operand = node["operand"]
        operand_type = node.get("inferred_type", "i32")  # fallback

        # 1) load the current variable
        self.controller.emit_expression(operand, out_lines)  # local.get $a

        # 2) If you want to print the 'old value' right away, it's already on stack.
        #    If you need to store it for re-use, do local.tee or something. Example:
        # out_lines.append(f"  local.tee $tempVarForOldValue")

        # 3) Now increment or decrement the variable in memory:
        #    a) re-load the variable:
        self.controller.emit_expression(operand, out_lines)  # local.get $a

        #    b) add or subtract 1
        if op == '++':
            if operand_type.startswith("i32"):
                out_lines.append("  i32.const 1")
                out_lines.append("  i32.add")
            elif operand_type.startswith("i64"):
                out_lines.append("  i64.const 1")
                out_lines.append("  i64.add")
            elif operand_type == "f64":
                out_lines.append("  f64.const 1.0")
                out_lines.append("  f64.add")
            # etc. for f32
        elif op == '--':
            # same logic with i32.const -1 or i32.sub
            if operand_type.startswith("i32"):
                out_lines.append("  i32.const 1")
                out_lines.append("  i32.sub")
            # etc.

        #    c) store back to variable
        # we assume operand is a local variable
        var_name = operand["name"]  # e.g. 'a'
        normalized = self.controller._normalize_local_name(var_name)
        out_lines.append(f"  local.set {normalized}")

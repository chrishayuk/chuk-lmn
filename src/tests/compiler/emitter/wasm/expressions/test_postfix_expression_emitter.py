# file: lmn/compiler/emitter/wasm/expressions/postfix_expression_emitter.py
class PostfixExpressionEmitter:
    """
    Emits code for postfix operators (a++, a--).
    In typical C-like semantics:
      1) The 'old value' of the operand is pushed on the stack 
         (for immediate usage or printing).
      2) Then we re-load the operand to do (operand +/- 1) -> local.set operand.
    """

    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure example:
          {
            "type": "PostfixExpression",
            "operator": "++" or "--",
            "operand": {
               "type": "VariableExpression",
               "name": "a",
               # optional "inferred_type": "i64"/"i32"/"f64"/"f32"
            }
          }
        """

        # 1) Push the "old value" of the operand for postfix usage:
        #    e.g. if we do 'print (a++)', the old value is what gets printed.
        self.controller.emit_expression(node["operand"], out_lines)

        # 2) Re-load the variable => we’ll do (operand + 1) or (operand - 1).
        self.controller.emit_expression(node["operand"], out_lines)

        # 3) Determine if operand is i32 or i64 (or possibly f32/f64).
        #    You can retrieve it from:
        #    - node["operand"].get("inferred_type")
        #    - or a call to self.controller.infer_type(node["operand"])
        operand_type = (
            node["operand"].get("inferred_type") or
            self.controller.infer_type(node["operand"])
        )

        # 4) Based on the operand type, emit the correct 'const 1' and add/sub instructions
        if operand_type == "i64":
            out_lines.append("  i64.const 1")
            if node["operator"] == "++":
                out_lines.append("  i64.add")
            else:  # "--"
                out_lines.append("  i64.sub")
        elif operand_type == "f64":
            # if you actually allow float postfix, you might do e.g. "f64.const 1.0", "f64.add"
            out_lines.append("  f64.const 1.0")
            if node["operator"] == "++":
                out_lines.append("  f64.add")
            else:
                out_lines.append("  f64.sub")
        elif operand_type == "f32":
            out_lines.append("  f32.const 1.0")
            if node["operator"] == "++":
                out_lines.append("  f32.add")
            else:
                out_lines.append("  f32.sub")
        else:
            # fallback: assume i32
            out_lines.append("  i32.const 1")
            if node["operator"] == "++":
                out_lines.append("  i32.add")
            else:
                out_lines.append("  i32.sub")

        # 5) local.set the variable to store the new value
        var_name = node["operand"].get("name", "unknownVar")
        normalized = self.controller._normalize_local_name(var_name)  # if your code does name normalization
        out_lines.append(f"  local.set {normalized}")

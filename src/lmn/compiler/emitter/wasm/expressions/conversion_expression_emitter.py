# file: lmn/compiler/emitter/wasm/expressions/conversion_expression_emitter.py
class ConversionExpressionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure example:
          {
            "type": "ConversionExpression",
            "from_type": "f32",
            "to_type": "f64",
            "source_expr": {...},    # Another expression node
            "inferred_type": ...     # optional
          }
        """

        # 1) Emit the source expression (dictionary-based)
        source_expr = node["source_expr"]
        self.controller.emit_expression(source_expr, out_lines)

        # 2) Insert the right WASM op
        from_t = node["from_type"]
        to_t = node["to_type"]

        if from_t == "f32" and to_t == "f64":
            out_lines.append("  f64.promote_f32")
        elif from_t == "f64" and to_t == "f32":
            out_lines.append("  f32.demote_f64")
        elif from_t == "i32" and to_t == "i64":
            out_lines.append("  i64.extend_i32_s")
        elif from_t == "i64" and to_t == "i32":
            # possibly i32.wrap_i64 or some error
            out_lines.append("  i32.wrap_i64")

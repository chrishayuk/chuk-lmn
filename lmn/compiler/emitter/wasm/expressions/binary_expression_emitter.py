# compiler/emitter/wasm/expressions/binary_expressionemitter.py
class BinaryExpressionEmitter:
    def __init__(self, controller):
        # set the controller
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node: { "type": "BinaryExpression", "operator": op, "left": ..., "right": ... }
        """
        op = node["operator"]
        left = node["left"]
        right = node["right"]

        # Emit left, then right
        self.controller.emit_expression(left, out_lines)
        self.controller.emit_expression(right, out_lines)

        if op == "+":
            out_lines.append('  i32.add')
        elif op == "-":
            out_lines.append('  i32.sub')
        elif op == "*":
            out_lines.append('  i32.mul')
        elif op == "<=":
            out_lines.append('  i32.le_s')
        elif op == "<":
            out_lines.append('  i32.lt_s')
        elif op == ">":
            out_lines.append('  i32.gt_s')
        elif op == ">=":
            out_lines.append('  i32.ge_s')
        elif op == "==":
            out_lines.append('  i32.eq')
        elif op == "!=":
            out_lines.append('  i32.ne')
        else:
            # fallback
            out_lines.append('  i32.add')

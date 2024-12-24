# file: compiler/emitter/wasm/expressions/binary_expression_emitter.py
class BinaryExpressionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure example:
          {
            "type": "BinaryExpression",
            "operator": "+",
            "inferred_type": "f64",  # for example
            "left":  {...},
            "right": {...}
          }
        """
        op = node["operator"]
        left = node["left"]
        right = node["right"]

        # 1) Emit code for left, then right => these push values on the stack
        self.controller.emit_expression(left, out_lines)
        self.controller.emit_expression(right, out_lines)

        # 2) Retrieve the final operation type from the node (already set by the type checker)
        op_type = node["inferred_type"]  # e.g. "i32", "i64", "f32", or "f64"

        # 3) Map the operator to the correct WASM instruction
        if op in ["+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!="]:
            # map operator
            wasm_op = self._map_operator(op, op_type)

            # output the operator
            out_lines.append(f"  {wasm_op}")
        else:
            # fallback
            out_lines.append(f"  {op_type}.add")

    def _map_operator(self, op, op_type):
        # same as before: return the correct e.g. "f64.add"
        mapping = {
            "+":  {
                "i32": "i32.add",
                "i64": "i64.add",
                "f32": "f32.add",
                "f64": "f64.add",
            },
            "-":  {
                "i32": "i32.sub",
                "i64": "i64.sub",
                "f32": "f32.sub",
                "f64": "f64.sub",
            },
            "*":  {
                "i32": "i32.mul",
                "i64": "i64.mul",
                "f32": "f32.mul",
                "f64": "f64.mul",
            },
            "/":  {
                "i32": "i32.div_s",
                "i64": "i64.div_s",
                "f32": "f32.div",
                "f64": "f64.div",
            },
            "<":  {
                "i32": "i32.lt_s",
                "i64": "i64.lt_s",
                "f32": "f32.lt",
                "f64": "f64.lt",
            },
            "<=": {
                "i32": "i32.le_s",
                "i64": "i64.le_s",
                "f32": "f32.le",
                "f64": "f64.le",
            },
            ">":  {
                "i32": "i32.gt_s",
                "i64": "i64.gt_s",
                "f32": "f32.gt",
                "f64": "f64.gt",
            },
            ">=": {
                "i32": "i32.ge_s",
                "i64": "i64.ge_s",
                "f32": "f32.ge",
                "f64": "f64.ge",
            },
            "==": {
                "i32": "i32.eq",
                "i64": "i64.eq",
                "f32": "f32.eq",
                "f64": "f64.eq",
            },
            "!=": {
                "i32": "i32.ne",
                "i64": "i64.ne",
                "f32": "f32.ne",
                "f64": "f64.ne",
            },
        }
        
        # return the mapping
        return mapping[op][op_type]

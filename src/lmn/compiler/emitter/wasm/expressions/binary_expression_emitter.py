# compiler/emitter/wasm/expressions/binary_expression_emitter.py
class BinaryExpressionEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node structure example:
          {
            "type": "BinaryExpression",
            "operator": "+",
            "left":  { ... },
            "right": { ... }
          }
        """

        op = node["operator"]
        left = node["left"]
        right = node["right"]

        # 1) Emit left, then right => push them on the stack
        self.controller.emit_expression(left, out_lines)
        self.controller.emit_expression(right, out_lines)

        # 2) Infer types for left/right (in a real compiler, you'd do this beforehand)
        #    This is a naive approach: we rely on 'controller.infer_type(...)'
        #    to return i32, i64, f32, or f64 for each sub-expression.
        left_type = self.controller.infer_type(left)
        right_type = self.controller.infer_type(right)

        # 3) Decide the final "operation type" based on left/right
        #    For simplicity: if either is float => float op
        #                    if either is i64 => i64 op
        #                    else => i32 op
        #    In real languages, you might do more precise unification or error out if mismatched.
        op_type = self._unify_types(left_type, right_type)

        # 4) Based on the operator, emit the correct Wasm instruction
        #    We'll just do i32.*, i64.*, f32.*, or f64.* as needed.
        if op in ["+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!="]:
            wasm_op = self._map_operator(op, op_type)
            out_lines.append(f"  {wasm_op}")
        else:
            # fallback
            out_lines.append(f"  {op_type}.add")  # e.g. i32.add if we don't recognize the op

    def _unify_types(self, left_t, right_t):
        """
        A naive function: 
          - If either is f64 => f64
          - else if either is f32 => f32
          - else if either is i64 => i64
          - else => i32
        """
        numeric_priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
        # pick the higher priority
        return left_t if numeric_priority[left_t] >= numeric_priority[right_t] else right_t

    def _map_operator(self, op, op_type):
        """
        Return the correct wasm operator, e.g. "f32.add", "i64.sub", etc.
        We'll handle +, -, *, /, <, <=, >, >=, ==, != for demonstration.
        """
        # We'll store a dict for each operator type
        # For add: i32.add / i64.add / f32.add / f64.add
        mapping = {
            "+": {
                "i32": "i32.add",
                "i64": "i64.add",
                "f32": "f32.add",
                "f64": "f64.add",
            },
            "-": {
                "i32": "i32.sub",
                "i64": "i64.sub",
                "f32": "f32.sub",
                "f64": "f64.sub",
            },
            "*": {
                "i32": "i32.mul",
                "i64": "i64.mul",
                "f32": "f32.mul",
                "f64": "f64.mul",
            },
            "/": {
                "i32": "i32.div_s",  # signed
                "i64": "i64.div_s",
                "f32": "f32.div",
                "f64": "f64.div",
            },
            "<": {
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
            ">": {
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
        return mapping[op][op_type]

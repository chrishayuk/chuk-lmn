# file: compiler/emitter/wasm/expressions/binary_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class BinaryExpressionEmitter:
    """
    Emits WebAssembly ops for binary expressions (+, -, *, /, //, %, <, <=, >, >=, ==, !=)
    on the new numeric lowered types: i32, i64, f32, f64.
    """

    def __init__(self, controller):
        """
        :param controller: your WasmEmitter or codegen context, with:
            - controller.emit_expression(expr, out_lines) to handle sub-expressions
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node example:
        {
          "type": "BinaryExpression",
          "operator": "+",  # or "-", "*", "/", "%", ...
          "left":  {...sub-AST...},
          "right": {...sub-AST...},
          "inferred_type": "f64"  # e.g. i32, i64, f32, f64
        }

        We'll:
          1) Emit left expr -> stack
          2) Emit right expr -> stack
          3) Append the correct WASM op (e.g. f64.add)
        """
        op = node["operator"]
        left = node["left"]
        right = node["right"]

        # 1) Emit code for left, then right
        self.controller.emit_expression(left, out_lines)
        self.controller.emit_expression(right, out_lines)

        # 2) The operation type from the type checker
        op_type = node.get("inferred_type", "i32")  # default if missing

        # 3) Map the operator to the correct WASM instruction
        wasm_op = self._map_operator(op, op_type)
        out_lines.append(f"  {wasm_op}")

    def _map_operator(self, op, op_type):
        """
        Maps (operator, op_type) to the correct WASM mnemonic.
        If not found, falls back or logs a warning/error.
        """
        mapping = {
            "+": {
                "i32": "i32.add", "i64": "i64.add",
                "f32": "f32.add", "f64": "f64.add",
            },
            "-": {
                "i32": "i32.sub", "i64": "i64.sub",
                "f32": "f32.sub", "f64": "f64.sub",
            },
            "*": {
                "i32": "i32.mul", "i64": "i64.mul",
                "f32": "f32.mul", "f64": "f64.mul",
            },
            "/": {
                "i32": "i32.div_s", "i64": "i64.div_s",
                "f32": "f32.div",   "f64": "f64.div",
            },
            "//": {  # treat as integer division for i32/i64, normal div for floats
                "i32": "i32.div_s", "i64": "i64.div_s",
                "f32": "f32.div",   "f64": "f64.div",
            },
            "%": {
                "i32": "i32.rem_s", "i64": "i64.rem_s",
                # No built-in remainder for float in core WASM
            },
            "<": {
                "i32": "i32.lt_s", "i64": "i64.lt_s",
                "f32": "f32.lt",   "f64": "f64.lt",
            },
            "<=": {
                "i32": "i32.le_s", "i64": "i64.le_s",
                "f32": "f32.le",   "f64": "f64.le",
            },
            ">": {
                "i32": "i32.gt_s", "i64": "i64.gt_s",
                "f32": "f32.gt",   "f64": "f64.gt",
            },
            ">=": {
                "i32": "i32.ge_s", "i64": "i64.ge_s",
                "f32": "f32.ge",   "f64": "f64.ge",
            },
            "==": {
                "i32": "i32.eq",   "i64": "i64.eq",
                "f32": "f32.eq",   "f64": "f64.eq",
            },
            "!=": {
                "i32": "i32.ne",   "i64": "i64.ne",
                "f32": "f32.ne",   "f64": "f64.ne",
            },
        }

        if op not in mapping or op_type not in mapping[op]:
            # fallback or error
            # raise ValueError(f"Unsupported operation '{op}' for type '{op_type}'")
            return f"{op_type}.add"  # fallback => e.g. i32.add

        return mapping[op][op_type]

# file: compiler/emitter/wasm/expressions/unary_expression_emitter.py

import logging

logger = logging.getLogger(__name__)

class UnaryExpressionEmitter:
    """
    Handles unary operators like '+' (do nothing), '-' (negate), or 'not' (logical negation)
    for the new lowered numeric types: i32, i64, f32, and f64.

    Example node:
      {
        "type": "UnaryExpression",
        "operator": "-",
        "operand": { "type": "LiteralExpression", "value": 123, "literal_type": "i32" },
        "inferred_type": "i32"
      }
    """

    def __init__(self, controller):
        """
        :param controller: the main WasmEmitter or similar,
                           providing emit_expression(...) and infer_type(...).
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        node => {
          "type": "UnaryExpression",
          "operator": "++" or "--" or "not" or ...
          "operand": AST node for operand,
          "inferred_type": "i32"/"i64"/"f32"/"f64"
        }
        We'll generate code for the operand, then apply the unary op.
        """
        op = node["operator"]  # e.g. "-", "not", "+"
        operand = node["operand"]

        # 1) Attempt constant-fold => if operand is a small int literal and op = '-', make it negative
        folded = self._try_constant_fold(node)
        if folded is not None:
            # folded => (wasmType, literal_value) => e.g. ("i32", -123)
            self._emit_constant(folded[0], folded[1], out_lines)
            return

        # 2) Otherwise, generate code for operand
        self.controller.emit_expression(operand, out_lines)

        # 3) Determine operand/inferred type
        operand_type = self._infer_operand_type(operand)

        # 4) Apply unary operator
        if op == "+":
            # unary plus => do nothing
            pass

        elif op == "-":
            # numeric negation
            if operand_type == "i32":
                out_lines.append("  i32.const -1")
                out_lines.append("  i32.mul")
            elif operand_type == "i64":
                out_lines.append("  i64.const -1")
                out_lines.append("  i64.mul")
            elif operand_type == "f32":
                out_lines.append("  f32.neg")
            elif operand_type == "f64":
                out_lines.append("  f64.neg")
            else:
                raise ValueError(f"Unsupported unary '-' for type {operand_type}")

        elif op == "not":
            # logical negation => eqz
            if operand_type == "i32":
                out_lines.append("  i32.eqz")
            elif operand_type == "i64":
                out_lines.append("  i64.eqz")  # (supported in many WASM toolchains)
            else:
                raise ValueError(f"Unsupported unary 'not' for type {operand_type}")

        else:
            raise ValueError(f"Unknown unary operator: '{op}'")

    def _infer_operand_type(self, operand_node):
        """
        Use the controller's type inference or direct operand 'inferred_type'.
        """
        return self.controller.infer_type(operand_node)

    def _try_constant_fold(self, unary_node):
        """
        If the operand is a LiteralExpression with an integer value,
        and the operator is '-', we can fold it into a negative literal.
        Returns (wasmType, foldedValue) if successful, else None.
        """
        op = unary_node["operator"]
        operand = unary_node["operand"]

        if op == "-" and operand["type"] == "LiteralExpression":
            val = operand.get("value")
            literal_t = operand.get("literal_type", "")  # e.g. "i32", "i64"
            if isinstance(val, int):
                # decide i32 or i64 (assuming smaller usage => i32, or check literal_t)
                if literal_t == "i64":
                    wasm_type = "i64"
                else:
                    wasm_type = "i32"
                return (wasm_type, -val)
        return None

    def _emit_constant(self, wasm_type, value, out_lines):
        """
        Emit e.g. "i32.const <value>" or "i64.const <value>" for folded literal.
        """
        if wasm_type == "i32":
            out_lines.append(f"  i32.const {value}")
        elif wasm_type == "i64":
            out_lines.append(f"  i64.const {value}")
        else:
            raise ValueError(f"_emit_constant not implemented for {wasm_type}")

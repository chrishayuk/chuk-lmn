# tests/emitter/wasm/statements/test_assignment_emitter.py
from lmn.compiler.emitter.wasm.statements.assignment_emitter import AssignmentEmitter

class MockController:
    def __init__(self):
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def _normalize_local_name(self, raw_name):
        return f"${raw_name}"

    def emit_expression(self, expr, out_lines):
        """
        Very simplified expression emitter for testing:
          - VariableExpression => i32.const 999
          - int literal => i32.const
          - big int => i64.const
          - float => i32.const <val>
        """
        etype = expr.get("type")
        if etype == "VariableExpression":
            # pretend we always output i32.const 999
            out_lines.append("  i32.const 999")
        elif etype == "LiteralExpression":
            val = expr.get("value", 0)
            if isinstance(val, int):
                if -2**31 <= val <= 2**31 - 1:
                    out_lines.append(f"  i32.const {val}")
                else:
                    out_lines.append(f"  i64.const {val}")
            elif isinstance(val, float):
                out_lines.append(f"  i32.const {val}")
            else:
                out_lines.append("  i32.const 0")
        else:
            out_lines.append("  i32.const 0")

    def infer_type(self, expr):
        """
        Very naive approach:
          - VariableExpression => i32 if unknown, else whatever is in func_local_map
          - int => i32 or i64
          - float => f32
        """
        etype = expr.get("type")
        if etype == "VariableExpression":
            name = expr.get("name", "")
            var_name = self._normalize_local_name(name)
            if var_name in self.func_local_map:
                return self.func_local_map[var_name]["type"]
            return "i32"

        elif etype == "LiteralExpression":
            val = expr.get("value", 0)
            if isinstance(val, int):
                if -2**31 <= val <= 2**31 - 1:
                    return "i32"
                else:
                    return "i64"
            elif isinstance(val, float):
                return "f32"
            else:
                return "i32"

        return "i32"

# tests/emitter/wasm/statements/test_for_emitter.py

import pytest
from lmn.compiler.emitter.wasm.statements.for_emitter import ForEmitter

class MockController:
    def __init__(self):
        self.func_local_map = {}
        self.local_counter = 0
        # If your SetEmitter or other logic expects new_locals:
        self.new_locals = set()

    def _normalize_local_name(self, raw_name):
        # "i" => "$i"
        return f"${raw_name}"

    def collect_local_declaration(self, var_name):
        # Register locals if not known
        if var_name not in self.func_local_map:
            self.func_local_map[var_name] = self.local_counter
            self.local_counter += 1

    def emit_expression(self, expr, out_lines):
        """
        Minimal example:
          - If "type" == "LiteralExpression", do "i32.const <value>"
          - If "type" == "VariableExpression", do "local.get $..."
          - Else fallback
        """
        expr_type = expr.get("type")
        if expr_type == "LiteralExpression":
            val = expr.get("value", 999)
            out_lines.append(f"  i32.const {val}")
        elif expr_type == "VariableExpression":
            var_name = self._normalize_local_name(expr["name"])
            out_lines.append(f"  local.get {var_name}")
        else:
            out_lines.append("  i32.const 999")

    def emit_statement(self, stmt, out_lines):
        """
        For the for-loop test, we can simply mock all statements as "i32.const 999".
        If you'd like the "SetStatement" to actually be processed, you can import
        the SetEmitter here and call it, but for this test, a simple stub suffices.
        """
        out_lines.append("  i32.const 999")


def test_simple_for_loop():
    fe = ForEmitter(MockController())
    node = {
        "type": "ForStatement",
        "variable": {"type": "VariableExpression", "name": "i"},
        "start_expr": {"type": "LiteralExpression", "value": 1},
        "end_expr":   {"type": "LiteralExpression", "value": 5},
        "step_expr":  None,  # defaults to +1
        "body": [
            {
                "type": "SetStatement",
                "variable": {"type": "VariableExpression", "name": "x"},
                "expression": {"type": "LiteralExpression", "value": 42}
            }
        ]
    }

    out = []
    fe.emit_for(node, out)
    combined = "\n".join(out)

    # Check initialization => i32.const 1 => local.set $i
    assert 'i32.const 1' in combined
    assert 'local.set $i' in combined

    # block/loop labels
    assert 'block $for_exit' in combined
    assert 'loop $for_loop' in combined

    # Condition => local.get $i, i32.const 5, i32.lt_s
    assert 'local.get $i' in combined
    assert 'i32.const 5' in combined
    assert 'i32.lt_s' in combined

    # Body => mock => "i32.const 999"
    assert 'i32.const 999' in combined

    # Step => local.get $i, i32.const 1, i32.add, local.set $i
    assert 'local.get $i' in combined
    assert 'i32.add' in combined
    assert 'local.set $i' in combined

    # Finally, we should see "br $for_loop"
    assert 'br $for_loop' in combined

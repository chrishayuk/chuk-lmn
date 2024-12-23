# tests/emitter/wasm/statements/test_set_emitter.py

import pytest
from lmn.compiler.emitter.wasm.statements.set_emitter import SetEmitter

class MockController:
    def __init__(self):
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def _normalize_local_name(self, raw_name):
        # e.g. "x" => "$x"
        return f"${raw_name}"

    def emit_expression(self, expr, out_lines):
        """
        If "type" is "LiteralExpression", do: "i32.const <value>"
        Otherwise, fallback to "i32.const 999"
        """
        if expr.get("type") == "LiteralExpression":
            val = expr.get("value", 0)
            out_lines.append(f"  i32.const {val}")
        else:
            out_lines.append("  i32.const 999")


def test_set_statement_new_var():
    emitter = SetEmitter(MockController())
    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "x"},
        "expression": {"type": "LiteralExpression", "value": 42}
    }

    out_lines = []
    emitter.emit_set(node, out_lines)
    combined = "\n".join(out_lines)

    # Expect:
    # 1) local is recorded -> that triggers (local $x i32) *in a real emitter*
    #    But here, we only record "new_locals" so a real FunctionEmitter might do (local $x i32).
    #    If your test literally expects "(local $x i32)" in 'combined', see note below.
    # 2) i32.const 42
    # 3) local.set $x

    # If your test looks specifically for "(local $x i32)", you can either:
    # A) Actually emit it here in the SetEmitter (some projects do).
    # B) Move it to FunctionEmitter's job. Adjust your test accordingly.

    # For demonstration, let's assume we *do* emit it here:
    # (You can remove or comment out if you only want to store in new_locals.)
    assert "  i32.const 42" in combined
    assert "local.set $x" in combined


def test_set_statement_existing_var():
    # We'll pre-populate func_local_map with '$y' so the code won't declare it again
    mock_ctrl = MockController()
    mock_ctrl.func_local_map['$y'] = 0
    mock_ctrl.local_counter = 1

    emitter = SetEmitter(mock_ctrl)
    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "y"},
        "expression": {"type": "LiteralExpression", "value": 99}
    }

    out_lines = []
    emitter.emit_set(node, out_lines)
    combined = "\n".join(out_lines)

    # We expect no re-declaration, just:
    # i32.const 99
    # local.set $y
    assert "(local $y i32)" not in combined
    assert "i32.const 99" in combined
    assert "local.set $y" in combined

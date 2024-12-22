# tests/emitter/wasm/statements/test_set_emitter.py
import pytest
from compiler.emitter.wasm.statements.set_emitter import SetEmitter

class MockController:
    def __init__(self):
        # Emulate the structure of WasmEmitter
        self.func_local_map = {}
        self.local_counter = 0

    def emit_expression(self, expr, out_lines):
        # For testing, assume we always push i32.const <value>
        val = expr.get("value", 0)
        out_lines.append(f"  i32.const {val}")

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

    # We expect:
    #   1) local declaration => (local $$x i32)
    #   2) i32.const 42
    #   3) local.set $$x

    assert "(local $$x i32)" in combined
    assert "i32.const 42" in combined
    assert "local.set $$x" in combined

def test_set_statement_existing_var():
    # This time we pre-populate func_local_map with 'y'
    mock_ctrl = MockController()
    mock_ctrl.func_local_map['y'] = 0  # variable 'y' already known
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

    # We expect:
    # - No local declaration => '(local $$y i32)' shouldn't appear (already declared)
    # - i32.const 99
    # - local.set $$y

    assert "(local $$y i32)" not in combined
    assert "i32.const 99" in combined
    assert "local.set $$y" in combined

# tests/emitter/wasm/statements/test_for_emitter.py
from compiler.emitter.wasm.statements.for_emitter import ForEmitter

class MockController:
    def __init__(self):
        # Emulate the structure of WasmEmitter
        self.func_local_map = {}
        self.local_counter = 0

    def emit_expression(self, expr, out_lines):
        # For testing, just pretend every expression is i32.const <some_value>
        # Real code would handle them properly.
        if "value" in expr:
            out_lines.append(f'  i32.const {expr["value"]}')
        elif expr["type"] == "VariableExpression":
            name = expr["name"]
            out_lines.append(f'  local.get $${name}')
        else:
            out_lines.append('  i32.const 999')

    def emit_statement(self, stmt, out_lines):
        # For simplicity, treat all statements as "i32.const 999"
        out_lines.append('  i32.const 999')

def test_simple_for_loop():
    fe = ForEmitter(MockController())
    node = {
        "type": "ForStatement",
        "variable": {"type": "VariableExpression", "name": "i"},
        "start_expr": {"type": "LiteralExpression", "value": 1},
        "end_expr": {"type": "LiteralExpression", "value": 5},
        "step_expr": None,  # defaults to +1
        "body": [
            {"type": "SetStatement", "variable": {"type": "VariableExpression", "name": "x"},
             "expression": {"type": "LiteralExpression", "value": 42}}
        ]
    }
    out = []
    fe.emit_for(node, out)
    combined = "\n".join(out)

    # Check that we see a local declared for i
    assert '(local $$i i32)' in combined

    # See i32.const 1 => local.set $i (initialization)
    assert 'i32.const 1' in combined
    assert 'local.set $$i' in combined

    # Check presence of block/loop labels
    assert 'block $for_exit' in combined
    assert 'loop $for_loop' in combined

    # Condition check => local.get $i, i32.const 5, i32.lt_s
    assert 'local.get $$i' in combined
    assert 'i32.const 5' in combined
    assert 'i32.lt_s' in combined

    # The body => we see "i32.const 999" from the mock statement
    # (We expect the controller emits i32.const 999 for any statement.)
    assert 'i32.const 999' in combined

    # The step => local.get $i, i32.const 1, i32.add => local.set $i
    assert 'local.get $$i' in combined
    assert 'i32.add' in combined
    # Just ensure local.set is there again
    assert 'local.set $$i' in combined

    # Finally, we should see "br $for_loop"
    assert 'br $for_loop' in combined

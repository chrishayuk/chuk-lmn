# tests/emitter/wasm/statements/test_for_emitter.py
import pytest
from compiler.emitter.wasm.statements.for_emitter import ForEmitter

class MockController:
    def __init__(self):
        # Emulate the structure of WasmEmitter
        self.func_local_map = {}
        self.local_counter = 0

    def collect_local_declaration(self, var_name):
        # If you are collecting local declarations at function-level:
        if var_name not in self.func_local_map:
            self.func_local_map[var_name] = self.local_counter
            self.local_counter += 1

    def emit_expression(self, expr, out_lines):
        # For testing, just pretend every expression is i32.const <some_value>.
        if "value" in expr:
            out_lines.append(f'  i32.const {expr["value"]}')
        elif expr["type"] == "VariableExpression":
            name = expr["name"]
            out_lines.append(f'  local.get ${name}')
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

    # If your updated ForEmitter no longer emits "(local $i i32)" inline,
    # comment out or remove the following if not relevant:
    # assert '(local $i i32)' in combined

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

    # This for-loop uses a blockless if => "if" ... "end"
    assert 'if' in combined
    assert 'end' in combined

    # Body => "i32.const 999"
    # (We expect "i32.const 999" from mock statements.)
    assert 'i32.const 999' in combined

    # Step => local.get $i, i32.const 1, i32.add => local.set $i
    # "local.get $i" again
    # "i32.const 1" 
    # "i32.add"
    # "local.set $i"
    assert 'local.get $i' in combined
    assert 'i32.add' in combined
    assert 'local.set $i' in combined

    # Finally, we should see "br $for_loop"
    assert 'br $for_loop' in combined

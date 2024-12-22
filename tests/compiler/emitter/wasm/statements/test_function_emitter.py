# tests/emitter/wasm/statements/test_function_emitter.py
from compiler.emitter.wasm.statements.function_emitter import FunctionEmitter

class MockController:
    def __init__(self):
        self.function_names = []
        self.func_local_map = {}
        self.local_counter = 0

    def emit_statement(self, stmt, out_lines):
        # For testing, pretend each statement just emits 'i32.const 999'
        out_lines.append('  i32.const 999')

def test_function_definition():
    fe = FunctionEmitter(MockController())
    node = {
        "type": "FunctionDefinition",
        "name": "foo",
        "params": ["x", "y"],
        "body": [
            {"type": "SetStatement", "variable": {"type": "VariableExpression", "name": "z"}, "expression": {"type": "LiteralExpression", "value": 42}}
        ]
    }
    out_lines = []
    fe.emit_function(node, out_lines)
    combined = "\n".join(out_lines)

    # We expect:
    #  1) (func $foo (param i32) (param i32) (result i32)
    assert '(func $foo (param i32) (param i32) (result i32)' in combined

    #  2) i32.const 999 from the mock statement
    assert 'i32.const 999' in combined

    #  3) fallback i32.const 0, return
    assert 'i32.const 0' in combined
    assert 'return' in combined

    #  4) closing paren => )
    assert ')' in combined

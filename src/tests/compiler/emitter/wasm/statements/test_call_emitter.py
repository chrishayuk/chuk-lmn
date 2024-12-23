# tests/emitter/wasm/statements/test_call_emitter.py
from lmn.compiler.emitter.wasm.statements.call_emitter import CallEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        # For testing, assume we push "i32.const <value>" for LiteralExpression
        # or "local.get $<name>" for VariableExpression, etc.
        if expr["type"] == "LiteralExpression":
            out_lines.append(f'  i32.const {expr["value"]}')
        elif expr["type"] == "VariableExpression":
            out_lines.append(f'  local.get ${expr["name"]}')
        else:
            out_lines.append('  i32.const 999')  # fallback

def test_call_statement():
    emitter = CallEmitter(MockController())
    node = {
        "type": "CallStatement",
        "name": "myFunction",
        "arguments": [
            { "type": "LiteralExpression", "value": 42 },
            { "type": "VariableExpression", "name": "x" }
        ]
    }

    out = []
    emitter.emit_call(node, out)
    combined = "\n".join(out)

    # We expect argument emission lines:
    #   i32.const 42
    #   local.get $x
    # Then a call:
    #   call $myFunction
    assert "i32.const 42" in combined
    assert "local.get $x" in combined
    assert "call $myFunction" in combined

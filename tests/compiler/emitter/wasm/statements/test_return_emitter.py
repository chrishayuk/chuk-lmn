# tests/emitter/wasm/statements/test_return_emitter.py
from compiler.emitter.wasm.statements.return_emitter import ReturnEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        # For testing, assume any expression node => "i32.const <value>"
        val = expr.get("value", 0)
        out_lines.append(f"  i32.const {val}")

def test_return_statement():
    re = ReturnEmitter(MockController())
    node = {
        "type": "ReturnStatement",
        "expression": { "type": "LiteralExpression", "value": 123 }
    }
    out_lines = []
    re.emit_return(node, out_lines)
    combined = "\n".join(out_lines)

    # We expect "i32.const 123" then "return"
    assert "i32.const 123" in combined
    assert "return" in combined

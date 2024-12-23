# tests/emitter/wasm/statements/test_print_emitter.py
from lmn.compiler.emitter.wasm.statements.print_emitter import PrintEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        # Mock: assume numeric expressions => "i32.const <value>"
        # e.g. expr = {"type": "LiteralExpression", "value": 999}
        val = expr.get("value", 0)
        out_lines.append(f"  i32.const {val}")

def test_print_statement():
    emitter = PrintEmitter(MockController())
    node = {
        "type": "PrintStatement",
        "expressions": [
            { "type": "LiteralExpression", "value": "Hello, World!" },  # string => skip
            { "type": "LiteralExpression", "value": 999 }               # numeric => emit
        ]
    }

    lines = []
    emitter.emit_print(node, lines)
    combined = "\n".join(lines)

    # We should see no emission for the string literal
    assert "Hello, World!" not in combined

    # For the numeric literal => i32.const 999 + call $print_i32
    assert "i32.const 999" in combined
    assert "call $print_i32" in combined

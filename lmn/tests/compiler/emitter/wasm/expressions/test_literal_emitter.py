import pytest
from compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter

class MockController:
    """If needed, we can have other methods here, but typically not used for a literal."""
    pass

def test_literal_expression():
    le = LiteralExpressionEmitter(MockController())
    node = {
      "type": "LiteralExpression",
      "value": 123
    }
    out = []
    le.emit(node, out)
    combined = "\n".join(out)

    # We expect a single line:  "i32.const 123"
    assert 'i32.const 123' in combined

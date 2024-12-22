from compiler.emitter.wasm.expressions.unary_expression_emitter import UnaryExpressionEmitter

class MockController:
    """Mock controller to simulate operand emission."""
    def emit_expression(self, expr, out_lines):
        # For testing, pretend every expression simply emits 'i32.const 777'
        out_lines.append('  i32.const 777')

def test_unary_plus():
    ue = UnaryExpressionEmitter(MockController())
    node = {
      "type": "UnaryExpression",
      "operator": "+",
      "operand": {"type": "LiteralExpression", "value": 42}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    # With unary plus, we expect:
    #   - The operand is emitted (mock => "i32.const 777")
    #   - No further instructions (since + is a no-op)
    assert 'i32.const 777' in combined
    assert 'i32.mul' not in combined
    assert 'i32.eqz' not in combined

def test_unary_minus():
    ue = UnaryExpressionEmitter(MockController())
    node = {
      "type": "UnaryExpression",
      "operator": "-",
      "operand": {"type": "LiteralExpression", "value": 42}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    # For unary minus, we expect:
    #   - The operand is emitted
    #   - "i32.const -1" then "i32.mul" (based on the simpler negate approach)
    assert 'i32.const 777' in combined
    assert 'i32.const -1' in combined
    assert 'i32.mul' in combined

def test_unary_not():
    ue = UnaryExpressionEmitter(MockController())
    node = {
      "type": "UnaryExpression",
      "operator": "not",
      "operand": {"type": "LiteralExpression", "value": 1}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    # For 'not', we expect i32.eqz
    assert 'i32.const 777' in combined
    assert 'i32.eqz' in combined

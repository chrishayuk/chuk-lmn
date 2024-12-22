from compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter

class MockController:
    """No special logic needed here unless your variable emitter calls back."""
    pass

def test_variable_expression():
    ve = VariableExpressionEmitter(MockController())
    node = {
      "type": "VariableExpression",
      "name": "x"
    }
    out = []
    ve.emit(node, out)
    combined = "\n".join(out)

    # We assume 'local.get $x' is emitted
    assert 'local.get $x' in combined

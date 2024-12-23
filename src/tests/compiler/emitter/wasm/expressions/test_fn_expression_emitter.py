import pytest
from lmn.compiler.emitter.wasm.expressions.fn_expression_emitter import FnExpressionEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        # For testing, pretend every argument is just 'i32.const 888'
        out_lines.append('  i32.const 888')

def test_fn_call():
    fe = FnExpressionEmitter(MockController())
    node = {
      "type": "FnExpression",
      "name": {"type": "VariableExpression", "name": "myFunction"},
      "arguments": [
         {"type": "LiteralExpression", "value": 42},
         {"type": "LiteralExpression", "value": 99}
      ]
    }
    out = []
    fe.emit_fn(node, out)
    combined = "\n".join(out)

    # We expect:
    #  - 2 argument evaluations => 'i32.const 888' repeated 2x
    #  - A call to $myFunction => 'call $myFunction'
    assert combined.count('i32.const 888') == 2
    assert 'call $myFunction' in combined

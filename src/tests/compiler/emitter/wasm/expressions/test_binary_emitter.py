# tests/emitter/wasm/expressions/test_binary_emitter.py
from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter

class MockController:
    def __init__(self):
        pass
    def emit_expression(self, expr, out_lines):
        out_lines.append('  i32.const 777')

def test_binary_add():
    be = BinaryExpressionEmitter(MockController())
    node = {
      "type": "BinaryExpression",
      "operator": "+",
      "left": { "type": "LiteralExpression", "value": 2 },
      "right": { "type": "LiteralExpression", "value": 3 }
    }
    out = []
    be.emit(node, out)
    combined = "\n".join(out)
    # we expect 2 calls to emit_expression => 'i32.const 777', 'i32.add'
    assert combined.count('i32.const 777') == 2
    assert 'i32.add' in combined

def test_binary_mul():
    be = BinaryExpressionEmitter(MockController())
    node = {
      "type": "BinaryExpression",
      "operator": "*",
      "left": { "type": "LiteralExpression", "value": 5 },
      "right": { "type": "LiteralExpression", "value": 6 }
    }
    out = []
    be.emit(node, out)
    combined = "\n".join(out)
    assert 'i32.mul' in combined

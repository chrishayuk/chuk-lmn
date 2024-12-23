# tests/emitter/wasm/statements/test_if_emitter.py
from lmn.compiler.emitter.wasm.statements.if_emitter import IfEmitter

class MockController:
    def __init__(self):
        pass

    def emit_expression(self, expr, out_lines):
        # For testing, pretend every condition is just "i32.const 1"
        out_lines.append('  i32.const 1')

    def emit_statement(self, stmt, out_lines):
        # For testing, pretend each statement is "i32.const 999"
        out_lines.append('  i32.const 999')

def test_if_no_else():
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression", "value": 42},
      "thenBody": [
         {"type": "SetStatement", "var": "x", "expr": {"type": "LiteralExpression", "value": 1}}
      ],
      "elseBody": []
    }
    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # We expect:
    #   i32.const 1   # condition
    #   if            # start of blockless if
    #   i32.const 999 # the statement body
    #   end
    assert 'i32.const 1' in combined
    assert 'if' in combined
    assert 'i32.const 999' in combined
    # Ensure there's an 'end'
    assert 'end' in combined
    # We should NOT see 'else'
    assert 'else' not in combined

def test_if_with_else():
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression", "value": 0},
      "thenBody": [
         {"type": "PrintStatement", "expressions": [{"type": "LiteralExpression", "value": "Hello"}]}
      ],
      "elseBody": [
         {"type": "SetStatement", "var": "y", "expr": {"type": "LiteralExpression", "value": 2}}
      ]
    }
    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # We expect:
    #   i32.const 1   # condition (mocked)
    #   if
    #     i32.const 999  # then statement
    #   else
    #     i32.const 999  # else statement
    #   end
    assert 'i32.const 1' in combined  # from the mock condition
    assert 'if' in combined
    assert 'else' in combined
    assert 'i32.const 999' in combined
    assert 'end' in combined

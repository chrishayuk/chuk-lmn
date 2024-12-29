# file: tests/emitter/wasm/statements/test_if_emitter.py

import pytest
from lmn.compiler.emitter.wasm.statements.if_emitter import IfEmitter

class MockController:
    def __init__(self):
        pass

    def emit_expression(self, expr, out_lines):
        # For testing, pretend every condition is "i32.const 1"
        out_lines.append('  i32.const 1')

    def emit_statement(self, stmt, out_lines):
        # For testing, pretend each statement is "i32.const 999"
        out_lines.append('  i32.const 999')


def test_if_no_else():
    """
    A simple IfStatement with no else_body or elseif_clauses
    """
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression", "value": 42},
      "then_body": [
         {"type": "LetStatement"}  # any statement
      ],
      # No else_body
    }

    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # Expect:
    #   i32.const 1        (mock condition)
    #   if
    #     i32.const 999    (mock statement)
    #   end

    assert 'i32.const 1' in combined  # from emit_expression
    assert 'if' in combined
    assert 'i32.const 999' in combined  # from emit_statement
    assert 'end' in combined
    # We should NOT see 'else'
    assert 'else' not in combined


def test_if_with_else():
    """
    An IfStatement with a standard else_body, no elseif_clauses
    """
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression", "value": 0},
      "then_body": [
         {"type": "PrintStatement"}
      ],
      "else_body": [
         {"type": "LetStatement"}
      ]
    }

    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # Expect:
    #   i32.const 1  (condition)
    #   if
    #     i32.const 999  (then)
    #   else
    #     i32.const 999  (else)
    #   end
    assert 'i32.const 1' in combined
    assert 'if' in combined
    assert 'else' in combined
    assert 'i32.const 999' in combined
    assert 'end' in combined


def test_if_with_single_elseif():
    """
    IfStatement with 1 elseif_clause and no final else_body
    """
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression", "value": 1},
      "then_body": [
         {"type": "PrintStatement"}
      ],
      "elseif_clauses": [
        {
          "type": "ElseIfClause",
          "condition": {"type": "LiteralExpression", "value": 2},
          "body": [
            {"type": "PrintStatement"}
          ]
        }
      ]
      # no else_body
    }

    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # We'll get something like:
    #   i32.const 1
    #   if
    #     i32.const 999
    #   else
    #     i32.const 1   (for the elseif condition)
    #     if
    #       i32.const 999
    #     else
    #     end
    #   end

    assert 'i32.const 1' in combined  # appears more than once
    assert 'if' in combined
    # We should see 'else'
    assert 'else' in combined
    # Should see two 'if' lines total
    assert combined.count('if') == 2
    # Should see two 'end' lines total
    assert combined.count('end') == 2


def test_if_with_multiple_elseif_and_else():
    """
    IfStatement with 2 elseif_clauses and a final else_body
    """
    emitter = IfEmitter(MockController())
    node = {
      "type": "IfStatement",
      "condition": {"type": "LiteralExpression"},
      "then_body": [
         {"type": "PrintStatement", "info": "then"}
      ],
      "elseif_clauses": [
        {
          "type": "ElseIfClause",
          "condition": {"type": "LiteralExpression"},
          "body": [
            {"type": "PrintStatement", "info": "elseif1"}
          ]
        },
        {
          "type": "ElseIfClause",
          "condition": {"type": "LiteralExpression"},
          "body": [
            {"type": "PrintStatement", "info": "elseif2"}
          ]
        }
      ],
      "else_body": [
        {"type": "LetStatement", "info": "final-else"}
      ]
    }

    out = []
    emitter.emit_if(node, out)
    combined = "\n".join(out)

    # Example expected structure:
    # i32.const 1
    # if
    #   i32.const 999
    # else
    #   i32.const 1  (elseif1 condition)
    #   if
    #     i32.const 999
    #   else
    #     i32.const 1 (elseif2 condition)
    #     if
    #       i32.const 999
    #     else
    #       i32.const 999  (the final else body)
    #     end
    #   end
    # end

    # Let's just do minimal checks:
    assert 'i32.const 1' in combined   # condition
    # We expect 3 if lines total (main, elseif1, elseif2)
    assert combined.count('if') == 3
    # We expect nested 'else'
    assert combined.count('else') == 3
    # We expect 'end' lines = 3
    assert combined.count('end') == 3
    # We also expect multiple 'i32.const 999' from all statements
    assert 'i32.const 999' in combined

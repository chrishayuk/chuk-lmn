# file: tests/compiler/emitter/test_conversion_expression_emitter.py

import pytest
from lmn.compiler.emitter.wasm.expressions.conversion_expression_emitter import ConversionExpressionEmitter

class MockController:
    """
    A minimal mock to handle the source expression.
    For instance, if you do 'emit_expression(node["source_expr"], out_lines)',
    we can produce something like 'i32.const 999' or 'f32.const 999.0'.
    """

    def __init__(self, source_instr="i32.const 999"):
        # We'll store a single line to represent the source expression emission.
        self.source_instr = source_instr

    def emit_expression(self, expr, out_lines):
        """
        Whenever the emitter tries to handle the source_expr, 
        we just append our mock line.
        """
        out_lines.append(f"  {self.source_instr}")


@pytest.mark.parametrize("from_type,to_type,expected_op", [
    ("f32", "f64", "f64.promote_f32"),
    ("f64", "f32", "f32.demote_f64"),
    ("i32", "i64", "i64.extend_i32_s"),
    ("i64", "i32", "i32.wrap_i64"),
    # Add more if your code handles them...
])
def test_conversion_expression(from_type, to_type, expected_op):
    """
    Verifies that ConversionExpressionEmitter emits the correct 
    WASM conversion instruction (e.g. f64.promote_f32, i32.wrap_i64, etc.).
    """
    # 1) Create the emitter with a trivial mock controller
    controller = MockController()
    ce = ConversionExpressionEmitter(controller)

    # 2) Build an AST node for ConversionExpression
    node = {
        "type": "ConversionExpression",
        "from_type": from_type,
        "to_type": to_type,
        "source_expr": {
            "type": "LiteralExpression",
            "value": 123.4  # Or anything else you like
        }
    }

    out_lines = []
    ce.emit(node, out_lines)

    combined = "\n".join(out_lines)

    # e.g. expecting something like:
    #   i32.const 999
    #   i64.extend_i32_s
    # or
    #   f32.const 999
    #   f64.promote_f32

    # 1) Check that we see the mock line for the source expression
    assert "999" in combined, (
        f"Expected mock source expression line '... 999' but got:\n{combined}"
    )
    # 2) Check that the conversion op is present
    assert expected_op in combined, (
        f"For from_type={from_type} -> to_type={to_type}, expected '{expected_op}', got:\n{combined}"
    )


def test_conversion_expression_with_different_source():
    """
    Demonstrates providing a different source instruction if you like.
    Now we actually expect 'f32.const 123.0' in the final code,
    plus 'f64.promote_f32' for the conversion from f32 to f64.
    """
    # Suppose the source is actually an f32 literal
    controller = MockController(source_instr="f32.const 123.0")
    ce = ConversionExpressionEmitter(controller)

    node = {
        "type": "ConversionExpression",
        "from_type": "f32",
        "to_type": "f64",
        "source_expr": {"type": "LiteralExpression", "value": 123.0}
    }

    out_lines = []
    ce.emit(node, out_lines)
    combined = "\n".join(out_lines)

    # We expect f32.const 123.0 from the mock, plus f64.promote_f32.
    # CHANGED: Now we ASSERT it is IN the output, not absent.
    assert "f32.const 123.0" in combined, (
        f"Expected the source line 'f32.const 123.0' but got:\n{combined}"
    )
    assert "f64.promote_f32" in combined, (
        f"Expected 'f64.promote_f32' for f32->f64, got:\n{combined}"
    )


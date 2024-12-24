import pytest
from lmn.compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter

class MockController:
    """If needed, we can have other methods here, but typically not used for a literal."""
    pass

@pytest.mark.parametrize("value, expected_instr", [
    # i32 tests
    (0, "i32.const 0"),
    (42, "i32.const 42"),
    (2147483647, "i32.const 2147483647"),  # Max 32-bit signed int

    # i64 tests (numbers just outside i32 range or obviously large)
    (2147483648, "i64.const 2147483648"),
    ("999999999999", "i64.const 999999999999"),

    # f32 tests (with 'f' suffix or small decimals)
    ("3.14f", "f32.const 3.14"),
    ("1.0f", "f32.const 1.0"),

    # f64 tests (decimals or exponent, no trailing 'f')
    ("3.14", "f64.const 3.14"),
    ("1e6", "f64.const 1e6"),
    ("2.71828", "f64.const 2.71828"),
])
def test_literal_expression(value, expected_instr):
    """
    This test covers a variety of literal values that should map to i32, i64, f32, or f64.
    We rely on the emitter code to figure out which WASM instruction to emit.
    """
    emitter = LiteralExpressionEmitter(MockController())
    node = {
        "type": "LiteralExpression",
        "value": value
    }
    out = []
    emitter.emit(node, out)
    combined = "\n".join(out)

    # Check that the correct instruction was emitted
    assert expected_instr in combined, f"Expected '{expected_instr}' but got:\n{combined}"

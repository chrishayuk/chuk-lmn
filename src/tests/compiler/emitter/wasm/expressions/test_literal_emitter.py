import pytest
from lmn.compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter

class MockController:
    """No special logic needed for literal emission tests."""
    pass

@pytest.mark.parametrize("value, inferred_type, expected_instr", [
    # --- i32 examples ---
    (0,       "i32", "i32.const 0"),
    (42,      "i32", "i32.const 42"),
    (-1,      "i32", "i32.const -1"),
    (2147483647,  "i32", "i32.const 2147483647"),  # Max 32-bit
    (-2147483648, "i32", "i32.const -2147483648"), # Min 32-bit

    # --- i64 examples ---
    (2147483648,    "i64", "i64.const 2147483648"),     # Just above i32 max
    (-2147483649,   "i64", "i64.const -2147483649"),    # Just below i32 min
    (999999999999,  "i64", "i64.const 999999999999"),
    (-999999999999, "i64", "i64.const -999999999999"),

    # --- f32 examples ---
    (0.0,     "f32", "f32.const 0.0"),
    (3.14,    "f32", "f32.const 3.14"),
    (-2.5,    "f32", "f32.const -2.5"),

    # --- f64 examples ---
    (0.0,     "f64", "f64.const 0.0"),
    (3.14,    "f64", "f64.const 3.14"),
    (-2.71828,"f64", "f64.const -2.71828"),
])
def test_literal_expression(value, inferred_type, expected_instr):
    """
    We assume the parser + typechecker already validated and typed these literals.
    The emitter just needs to produce i32.const, i64.const, f32.const, or f64.const
    with the final numeric value.
    """
    emitter = LiteralExpressionEmitter(MockController())

    node = {
        "type": "LiteralExpression",
        "value": value,               # A Python int or float
        "inferred_type": inferred_type
    }

    out = []
    emitter.emit(node, out)
    combined = "\n".join(out)

    # Check that 'expected_instr' is a substring in 'combined'
    assert expected_instr in combined, (
        f"Expected '{expected_instr}' but got:\n{combined}"
    )

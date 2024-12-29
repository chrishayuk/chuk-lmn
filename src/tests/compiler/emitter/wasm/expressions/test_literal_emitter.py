# file: tests/compiler/emitter/test_literal_expression_emitter.py

import pytest
from lmn.compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter

class MockController:
    """
    A trivial mock for the emitter's controller. 
    This is enough for testing LiteralExpressionEmitter, 
    which doesn't need to call back into the controller 
    for sub-expressions anyway.
    """
    pass

@pytest.mark.parametrize("value, inferred_type, expected_instr", [
    # --- i32 examples ---
    (0,       "i32", "i32.const 0"),
    (42,      "i32", "i32.const 42"),
    (-1,      "i32", "i32.const -1"),
    (2147483647,  "i32", "i32.const 2147483647"),   # Max 32-bit
    (-2147483648, "i32", "i32.const -2147483648"),  # Min 32-bit

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
    Tests that LiteralExpressionEmitter emits the correct Wasm instruction 
    for a given (value, inferred_type) pair.

    For instance, if inferred_type = "i32" and value = 42, 
    we expect "i32.const 42".
    """
    # 1) Instantiate the emitter with a trivial mock controller.
    emitter = LiteralExpressionEmitter(MockController())

    # 2) Construct a minimal AST node for a literal.
    node = {
        "type": "LiteralExpression",
        "value": value,
        "inferred_type": inferred_type
    }

    # 3) Emit the instructions.
    out_lines = []
    emitter.emit(node, out_lines)

    # 4) Convert to a single string for easier debugging.
    combined_output = "\n".join(out_lines)

    # 5) Ensure the expected instruction is present.
    #    If your emitter produces exactly one line, you might do an equality check 
    #    rather than a substring check.
    assert expected_instr in combined_output, (
        f"Expected '{expected_instr}' but got:\n{combined_output}"
    )

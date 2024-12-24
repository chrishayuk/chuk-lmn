import pytest
from lmn.compiler.emitter.wasm.expressions.unary_expression_emitter import UnaryExpressionEmitter

class MockController:
    """
    Mock controller to simulate operand emission for different WASM types.
    We'll store wasm_type in the constructor so the test can parametrize
    which type we pretend the operand is.
    """
    def __init__(self, wasm_type="i32"):
        self.wasm_type = wasm_type

    def emit_expression(self, expr, out_lines):
        """
        Pretend each operand expression always emits a single '[type].const 777' line,
        where [type] is i32/i64/f32/f64, based on self.wasm_type.
        """
        if self.wasm_type == "i32":
            out_lines.append('  i32.const 777')
        elif self.wasm_type == "i64":
            out_lines.append('  i64.const 777')
        elif self.wasm_type == "f32":
            out_lines.append('  f32.const 777')
        elif self.wasm_type == "f64":
            out_lines.append('  f64.const 777')
        else:
            raise ValueError(f"Unknown wasm type: {self.wasm_type}")
        
    def infer_type(self, node):
      """
      If your emitter code calls 'controller.infer_type(...)', you must define
      this here in the mock. For tests, you can always return the same 'wasm_type'
      that was set in the constructor, or parse something from 'node'.
      """
      return self.wasm_type


def test_unary_plus_i32():
    """
    A simple test for unary plus with i32.
    We expect that we only emit the operand (mock => i32.const 777),
    and no extra instructions.
    """
    ue = UnaryExpressionEmitter(MockController("i32"))
    node = {
        "type": "UnaryExpression",
        "operator": "+",
        "operand": {"type": "LiteralExpression", "value": 42}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    assert "i32.const 777" in combined
    # '+' => no additional instructions
    assert "i32.const -1" not in combined
    assert "i32.eqz" not in combined


def test_unary_minus_i32():
    """
    A simple test for unary minus with i32.
    We expect: i32.const 777, then i32.const -1, then i32.mul
    """
    ue = UnaryExpressionEmitter(MockController("i32"))
    node = {
        "type": "UnaryExpression",
        "operator": "-",
        "operand": {"type": "LiteralExpression", "value": 42}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    assert "i32.const 777" in combined
    assert "i32.const -1" in combined
    assert "i32.mul" in combined


def test_unary_not_i32():
    """
    A simple test for unary NOT (boolean negation) with i32.
    We expect: i32.const 777, then i32.eqz
    """
    ue = UnaryExpressionEmitter(MockController("i32"))
    node = {
        "type": "UnaryExpression",
        "operator": "not",
        "operand": {"type": "LiteralExpression", "value": 1}
    }
    out = []
    ue.emit(node, out)
    combined = "\n".join(out)

    assert "i32.const 777" in combined
    assert "i32.eqz" in combined


@pytest.mark.parametrize("operator, wasm_type, expected_lines", [
    # --- i32 cases ---
    ("+",  "i32", [
        "  i32.const 777"  # unary plus => no extra instructions
    ]),
    ("-",  "i32", [
        "  i32.const 777",
        "  i32.const -1",
        "  i32.mul"
    ]),
    ("not","i32", [
        "  i32.const 777",
        "  i32.eqz"
    ]),

    # --- i64 cases ---
    ("+",  "i64", [
        "  i64.const 777"
    ]),
    ("-",  "i64", [
        "  i64.const 777",
        "  i64.const -1",
        "  i64.mul"
    ]),
    ("not","i64", [
        "  i64.const 777",
        "  i64.eqz"
    ]),

    # --- f32 cases ---
    ("+",  "f32", [
        "  f32.const 777"
    ]),
    ("-",  "f32", [
        "  f32.const 777",
        "  f32.neg"
    ]),
    # "not" for floats not implemented in our emitter => skip

    # --- f64 cases ---
    ("+",  "f64", [
        "  f64.const 777"
    ]),
    ("-",  "f64", [
        "  f64.const 777",
        "  f64.neg"
    ]),
    # "not" for floats => skip
])
def test_unary_extended(operator, wasm_type, expected_lines):
    """
    A parametrized test covering unary operators (+, -, not) across
    i32, i64, f32, and f64 operand types.
    """
    ue = UnaryExpressionEmitter(MockController(wasm_type=wasm_type))
    node = {
        "type": "UnaryExpression",
        "operator": operator,
        "operand": {"type": "LiteralExpression", "value": 42}
    }
    out = []
    ue.emit(node, out)

    # Compare the actual lines vs expected lines
    assert out == expected_lines, (
        f"\nFor operator='{operator}', wasm_type='{wasm_type}'\n"
        f"Expected lines:\n{expected_lines}\n\nBut got:\n{out}\n"
    )

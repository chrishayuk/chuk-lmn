# file: tests/emitter/wasm/statements/test_return_emitter.py

import pytest
from lmn.compiler.emitter.wasm.statements.return_emitter import ReturnEmitter

class MockController:
    """
    Simplified controller for testing ReturnEmitter.
    We assume:
      - If expr is present => i32.const <value>
      - If no expr => we do nothing before 'return'
    """

    def emit_expression(self, expr, out_lines):
        # For testing, assume any expression node => "i32.const <expr_value>"
        val = expr.get("value", 0)
        out_lines.append(f"  i32.const {val}")


@pytest.mark.parametrize("expr_value, expected_snippet", [
    # 1) Typical integer
    (123, "i32.const 123"),
    # 2) Negative int
    (-1, "i32.const -1"),
    # 3) Large int
    (999999999999, "i32.const 999999999999"),
    # 4) No expression => no i32.const
    (None, None),
])
def test_return_statement(expr_value, expected_snippet):
    """
    Parameterized test for ReturnStatement with different expr values.
      - If expr_value is an integer, we expect i32.const <expr_value>.
      - If expr_value is None, we skip that step.
    In all cases, we want 'return' in the output.
    """
    re = ReturnEmitter(MockController())

    # Build the AST node
    node = { "type": "ReturnStatement" }
    if expr_value is not None:
        node["expression"] = {
            "type": "LiteralExpression",
            "value": expr_value
        }

    out_lines = []
    re.emit_return(node, out_lines)
    combined = "\n".join(out_lines)

    # If there's an expression, check the i32.const line
    if expr_value is not None:
        assert expected_snippet in combined, (
            f"For expr_value={expr_value}, expected '{expected_snippet}' in:\n{combined}"
        )
    else:
        # No expression => no i32.const
        assert "i32.const" not in combined, f"Did not expect any i32.const in:\n{combined}"

    # Always expect 'return'
    assert "return" in combined, f"Expected 'return' in:\n{combined}"

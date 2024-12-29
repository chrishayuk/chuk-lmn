import pytest
from lmn.compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter

class MockController:
    """No special logic needed here unless your variable emitter calls back."""
    pass

@pytest.mark.parametrize("var_name, expected_snippet", [
    # Basic name
    ("x", "local.get $x"),

    # A typical user-defined variable
    ("myVar", "local.get $myVar"),

    # If your emitter normalizes '$$thing' => '$thing'
    ("$$thing", "local.get $thing"),

    # If a name already starts with a single '$', keep it as is
    ("$already", "local.get $already"),
])
def test_variable_expression(var_name, expected_snippet):
    """
    Verify that the emitter produces the correct 'local.get $...' instruction,
    including any name normalization your emitter might do.

    For example:
      - "x" => "local.get $x"
      - "$$thing" => "local.get $thing"
      - "$already" => "local.get $already"
    """
    # 1) Instantiate the emitter with a trivial mock controller
    ve = VariableExpressionEmitter(MockController())

    # 2) Build a minimal AST node for a variable expression
    node = {
      "type": "VariableExpression",
      "name": var_name
    }

    # 3) Emit the instructions
    out_lines = []
    ve.emit(node, out_lines)

    # 4) Join them for easy assertions
    combined_output = "\n".join(out_lines)

    # 5) Check that 'local.get $var' is in the output
    assert expected_snippet in combined_output, (
        f"For var_name='{var_name}', expected snippet '{expected_snippet}'\n"
        f"Got:\n{combined_output}"
    )

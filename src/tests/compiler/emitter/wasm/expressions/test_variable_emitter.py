import pytest
from lmn.compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter

class MockController:
    """No special logic needed here unless your variable emitter calls back."""
    pass

@pytest.mark.parametrize("var_name, expected_snippet", [
    # Basic name
    ("x", "local.get $x"),
    # Typical user-defined variable
    ("myVar", "local.get $myVar"),
    # If your emitter normalizes '$$thing' => '$thing'
    ("$$thing", "local.get $thing"),
    # If a name already starts with one '$', keep it as is
    ("$already", "local.get $already"),
])
def test_variable_expression(var_name, expected_snippet):
    """
    Verify that the emitter produces the correct local.get instruction,
    including any name normalization your emitter might do.
    """
    ve = VariableExpressionEmitter(MockController())
    node = {
      "type": "VariableExpression",
      "name": var_name
    }
    out = []
    ve.emit(node, out)

    combined = "\n".join(out)

    # We assume something like 'local.get $x' or 'local.get $thing'
    assert expected_snippet in combined, (
        f"For var_name='{var_name}', expected snippet '{expected_snippet}'\n"
        f"Got:\n{combined}"
    )

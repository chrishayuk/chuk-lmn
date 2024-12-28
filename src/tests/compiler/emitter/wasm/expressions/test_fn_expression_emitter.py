import pytest
from lmn.compiler.emitter.wasm.expressions.fn_expression_emitter import FnExpressionEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        """
        For testing, we pretend every argument is just 'i32.const 888'.
        If you'd like to vary by expr["value"] or expr["inferred_type"],
        you can enhance this logic accordingly.
        """
        out_lines.append("  i32.const 888")

@pytest.mark.parametrize("func_name", ["myFunction", "someFunc", "calcSomething"])
@pytest.mark.parametrize("arg_count", [0, 1, 2, 3])
def test_fn_call(func_name, arg_count):
    """
    Tests calling function 'func_name' with 'arg_count' arguments.
    Each argument should produce one 'i32.const 888' line,
    then we expect a 'call $func_name'.
    """
    controller = MockController()
    fe = FnExpressionEmitter(controller)

    # Build an AST node for a FnExpression
    node = {
        "type": "FnExpression",
        "name": {
            "type": "VariableExpression",
            "name": func_name
        },
        "arguments": []
    }

    # Add 'arg_count' placeholders
    for i in range(arg_count):
        node["arguments"].append({
            "type": "LiteralExpression",
            "value": i  # your real code might store the actual value
        })

    out = []
    fe.emit_fn(node, out)

    # Convert to a single string for easy debugging
    combined = "\n".join(out)

    # We expect exactly 'arg_count' occurrences of 'i32.const 888'
    # plus one line 'call $func_name'.
    assert combined.count('i32.const 888') == arg_count, (
        f"Expected {arg_count} lines of 'i32.const 888', got:\n{combined}"
    )

    # Ensure 'call $func_name' appears exactly once.
    expected_call = f"call ${func_name}"
    assert combined.count(expected_call) == 1, (
        f"Expected exactly one '{expected_call}', got:\n{combined}"
    )

def test_fn_call_with_specific_arguments():
    """
    Demonstrates how you might vary the argument instructions
    if you want the mock to handle certain values differently.
    For now, we still do 'i32.const 888', but let's see
    the function name is 'myFunction2'.
    """
    controller = MockController()
    fe = FnExpressionEmitter(controller)

    node = {
        "type": "FnExpression",
        "name": {"type": "VariableExpression", "name": "myFunction2"},
        "arguments": [
            {"type": "LiteralExpression", "value": 42},
            {"type": "LiteralExpression", "value": 99},
        ]
    }

    out = []
    fe.emit_fn(node, out)
    combined = "\n".join(out)

    # We expect 2 lines with i32.const 888
    assert combined.count("i32.const 888") == 2
    # and a final line 'call $myFunction2'
    assert "call $myFunction2" in combined

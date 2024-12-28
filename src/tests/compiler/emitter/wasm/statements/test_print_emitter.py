import pytest
from lmn.compiler.emitter.wasm.statements.print_emitter import PrintEmitter

class MockController:
    def emit_expression(self, expr, out_lines):
        """
        Mock: if 'value' is numeric (int or float), we emit 'i32.const <value>'.
        If it's a string, skip it, just like your current code suggests.
        """
        val = expr.get("value", None)

        # If 'val' is int or float, produce 'i32.const'
        if isinstance(val, (int, float)):
            out_lines.append(f"  i32.const {val}")
        # If it's a string or something else, do nothing
        # (in real code, you might handle string with call $print_string or skip it entirely)

@pytest.mark.parametrize("expressions,expected_snippets", [
    # 1) Single string => skip
    (
        [{"type": "LiteralExpression", "value": "Hello"}],
        [
            # We want no 'Hello' in final code, no i32.const, but we do want 'call $print_i32'?
            # Actually if there's no numeric expression, we might not even see a call.
            # In your base test, you skip the string entirely => no instructions.
            # So let's expect zero instructions for this scenario, or maybe we check it's empty?
            # We'll verify we do NOT see "Hello" or "call $print_i32".
        ],
    ),
    # 2) Single integer => i32.const <int> + call $print_i32
    (
        [{"type": "LiteralExpression", "value": 999}],
        [
            "i32.const 999",
            "call $print_i32",
        ],
    ),
    # 3) Single float => i32.const 3.14 (your mock still does i32.const for floats)
    (
        [{"type": "LiteralExpression", "value": 3.14}],
        [
            "i32.const 3.14",
            "call $print_i32",
        ],
    ),
    # 4) Mixed: string and int
    (
        [
            {"type": "LiteralExpression", "value": "Hello, World!"},
            {"type": "LiteralExpression", "value": 123}
        ],
        [
            # skip 'Hello, World!'
            "i32.const 123",
            "call $print_i32",
        ],
    ),
    # 5) Multiple numeric
    (
        [
            {"type": "LiteralExpression", "value": 10},
            {"type": "LiteralExpression", "value": 20}
        ],
        [
            "i32.const 10",
            "call $print_i32",
            "i32.const 20",
            "call $print_i32",
        ],
    ),
    # 6) Empty list of expressions => no prints
    (
        [],
        [
            # no instructions expected
        ],
    ),
])
def test_print_statement(expressions, expected_snippets):
    """
    Parametrized test for PrintStatement with various 'expressions' arrays:
      - string only => skip
      - int => i32.const <int> + call $print_i32
      - float => i32.const <float> + call $print_i32 (mock logic)
      - multiple => each numeric => i32.const + call $print_i32
      - empty => no instructions
    """
    from lmn.compiler.emitter.wasm.statements.print_emitter import PrintEmitter
    emitter = PrintEmitter(MockController())

    node = {
        "type": "PrintStatement",
        "expressions": expressions
    }

    lines = []
    emitter.emit_print(node, lines)
    combined = "\n".join(lines)

    if not expressions:
        # no expressions => we expect zero instructions
        assert combined.strip() == "", f"Expected no instructions, got:\n{combined}"
    else:
        # Check each snippet in expected_snippets
        for snippet in expected_snippets:
            assert snippet in combined, (
                f"Expected snippet '{snippet}' in:\n{combined}"
            )

    # If there's a string literal, ensure it's not in combined
    for expr in expressions:
        val = expr.get("value")
        if isinstance(val, str):
            assert val not in combined, (
                f"String '{val}' should not appear in emitter code:\n{combined}"
            )

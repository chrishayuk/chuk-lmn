import pytest
from lmn.compiler.emitter.wasm.statements.set_emitter import SetEmitter

class MockController:
    def __init__(self):
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def _normalize_local_name(self, raw_name):
        # e.g. "x" => "$x"
        return f"${raw_name}"

    def emit_expression(self, expr, out_lines):
        """
        If "type" is "LiteralExpression", do: "i32.const <value>"
        Otherwise, fallback to "i32.const 999"
        """
        if expr.get("type") == "LiteralExpression":
            val = expr.get("value", 0)
            out_lines.append(f"  i32.const {val}")
        else:
            out_lines.append("  i32.const 999")

    def infer_type(self, expr):
        """
        A naive inference method. If it's a numeric literal with a decimal, return 'f32'.
        Else, if it fits i32 range, 'i32'. Otherwise 'i64'.
        (Or adapt to your real logic.)
        """
        if expr.get("type") == "LiteralExpression":
            value = expr.get("value", 0)
            val_str = str(value)
            if "." in val_str:
                return "f32"
            else:
                # Check if value is in i32 range
                int_val = int(value)
                if abs(int_val) > 2147483647:
                    return "i64"
                return "i32"
        # fallback
        return "i32"


def test_set_statement_new_var():
    """
    Test creating a brand new variable 'x'. We expect:
     - The variable is recorded in func_local_map with a type
     - i32.const 42
     - local.set $x
    """
    controller = MockController()
    emitter = SetEmitter(controller)
    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "x"},
        "expression": {"type": "LiteralExpression", "value": 42}
    }

    out_lines = []
    emitter.emit_set(node, out_lines)
    combined = "\n".join(out_lines)

    # Check the output instructions
    assert "  i32.const 42" in combined
    assert "local.set $x" in combined

    # Check that x was added to func_local_map
    assert "$x" in controller.func_local_map
    # If you're storing an object/dict with {'index': idx, 'type': ...}, check that
    info = controller.func_local_map["$x"]
    assert info["type"] == "i32", f"Expected x to be i32, got {info['type']}"

    # Also check new_locals
    assert "$x" in controller.new_locals


def test_set_statement_existing_var():
    """
    We'll pre-populate func_local_map with '$y' so the code won't declare it again.
    The expression is also i32, so no conflict in type. We expect:
      i32.const 99
      local.set $y
    and no mention of new locals.
    """
    mock_ctrl = MockController()
    # Suppose we store: { 'index': 0, 'type': 'i32' }
    mock_ctrl.func_local_map["$y"] = {"index": 0, "type": "i32"}
    mock_ctrl.local_counter = 1

    emitter = SetEmitter(mock_ctrl)
    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "y"},
        "expression": {"type": "LiteralExpression", "value": 99}
    }

    out_lines = []
    emitter.emit_set(node, out_lines)
    combined = "\n".join(out_lines)

    assert "i32.const 99" in combined
    assert "local.set $y" in combined

    # Ensure we didn't re-add $y to new_locals
    assert "$y" not in mock_ctrl.new_locals


def test_set_statement_new_var_float():
    """
    Test a new variable 'fvar' assigned a float literal (e.g. 3.14).
    We'll see infer_type => f32.
    """
    controller = MockController()
    emitter = SetEmitter(controller)
    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "fvar"},
        "expression": {"type": "LiteralExpression", "value": 3.14}
    }

    out_lines = []
    emitter.emit_set(node, out_lines)
    combined = "\n".join(out_lines)

    # By default our MockController emits i32.const for any literal in emit_expression,
    # but let's just check the final lines. (If we wanted f32.const, we'd adjust emit_expression)
    assert "i32.const 3.14" in combined, "MockController always uses i32.const <value>, so it's textual."
    assert "local.set $fvar" in combined

    # Check type in func_local_map
    info = controller.func_local_map["$fvar"]
    assert info["type"] == "f32", f"Expected fvar to be f32, got {info['type']}"
    assert "$fvar" in controller.new_locals


def test_set_statement_type_conflict():
    """
    Check if we handle or ignore a type conflict:
     - First set z => i32
     - Then set z => a large number => i64
    Currently the code just 'pass'es, but let's demonstrate how we'd detect a mismatch.
    """
    controller = MockController()
    emitter = SetEmitter(controller)

    # First assignment => z = 100 => i32
    node1 = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "z"},
        "expression": {"type": "LiteralExpression", "value": 100}
    }
    out_lines1 = []
    emitter.emit_set(node1, out_lines1)

    # Second assignment => z = 999999999999 => i64
    node2 = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "z"},
        "expression": {"type": "LiteralExpression", "value": 999999999999}
    }
    out_lines2 = []
    emitter.emit_set(node2, out_lines2)

    # Check the final lines are correct for each assignment
    combined1 = "\n".join(out_lines1)
    combined2 = "\n".join(out_lines2)

    assert "i32.const 100" in combined1
    assert "local.set $z" in combined1

    # second
    assert "i32.const 999999999999" in combined2  # Mock, but let's see it.
    assert "local.set $z" in combined2

    # Type checks
    first_info = controller.func_local_map["$z"]
    assert first_info["type"] == "i32", "After first assignment, z is i32"

    # But your second assignment code has 'pass' if there's a mismatch. 
    # In a real scenario, you might unify or throw an error. Here it remains i32.
    # Let's confirm it didn't get overwritten:
    second_info = controller.func_local_map["$z"]
    assert second_info["type"] == "i32", (
        "Your code hasn't updated the type. If you want to unify or throw error, you'd do so in the else-block."
    )

    # If you had logic to unify, you'd expect second_info["type"] == "i64" or an error message, etc.


def test_set_statement_assign_var():
    """
    If the expression is just a variable reference, e.g. set w x
    Then we check the type is inherited from x if new, or confirm it matches if existing.
    """
    controller = MockController()
    controller.func_local_map["$x"] = {"index": 0, "type": "i32"}
    emitter = SetEmitter(controller)

    node = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "w"},
        "expression": {"type": "VariableExpression", "name": "x"}
    }
    out_lines = []
    emitter.emit_set(node, out_lines)

    combined = "\n".join(out_lines)
    assert "  i32.const 999" in combined  # from mock emit_expression fallback
    assert "local.set $w" in combined

    # Since w didn't exist, we infer type from the expression. But our mock 'infer_type' doesn't
    # handle variable references properly (it returns i32 by default).
    # If you want real logic, you'd do something like:
    #  - w_type = controller.func_local_map["$x"]["type"]
    #  - or unify w with x
    info = controller.func_local_map["$w"]
    assert info["type"] == "i32"


def test_set_statement_multiple_new_locals():
    """
    If we do set a, then set b, each new var increments local_counter, 
    and each goes in new_locals.
    """
    controller = MockController()
    emitter = SetEmitter(controller)

    # set a
    node_a = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "a"},
        "expression": {"type": "LiteralExpression", "value": 1}
    }
    out_a = []
    emitter.emit_set(node_a, out_a)

    # set b
    node_b = {
        "type": "SetStatement",
        "variable": {"type": "VariableExpression", "name": "b"},
        "expression": {"type": "LiteralExpression", "value": 2}
    }
    out_b = []
    emitter.emit_set(node_b, out_b)

    # checks
    assert controller.local_counter == 2, f"Expected 2 new locals, got {controller.local_counter}"
    assert "$a" in controller.func_local_map
    assert "$b" in controller.func_local_map
    assert "$a" in controller.new_locals
    assert "$b" in controller.new_locals

    # 'a' lines
    assert "  i32.const 1" in "\n".join(out_a)
    assert "local.set $a" in "\n".join(out_a)

    # 'b' lines
    assert "  i32.const 2" in "\n".join(out_b)
    assert "local.set $b" in "\n".join(out_b)

import pytest
from lmn.compiler.emitter.wasm.statements.assignment_emitter import AssignmentEmitter

class MockController:
    def __init__(self):
        self.func_local_map = {}
        self.local_counter = 0
        self.new_locals = set()

    def _normalize_local_name(self, raw_name):
        return f"${raw_name}"

    def emit_expression(self, expr, out_lines):
        """
        Very simplified expression emitter for testing:
          - VariableExpression => i32.const 999
          - int literal => i32.const or i64.const if out of i32 range
          - float => i32.const <val>
        """
        if not expr:
            out_lines.append("  i32.const 0")
            return

        etype = expr.get("type")
        if etype == "VariableExpression":
            out_lines.append("  i32.const 999")
        elif etype == "LiteralExpression":
            val = expr.get("value", 0)
            if isinstance(val, int):
                if -2**31 <= val <= 2**31 - 1:
                    out_lines.append(f"  i32.const {val}")
                else:
                    out_lines.append(f"  i64.const {val}")
            elif isinstance(val, float):
                out_lines.append(f"  i32.const {val}")
            else:
                out_lines.append("  i32.const 0")
        else:
            out_lines.append("  i32.const 0")

    def infer_type(self, expr):
        """
        Very naive approach:
          - If a variable is declared, return that type; else "i32".
          - int => i32 if in range, else i64
          - float => f32
        """
        if not expr:
            return "i32"

        etype = expr.get("type")
        if etype == "VariableExpression":
            name = expr.get("name", "")
            var_name = self._normalize_local_name(name)
            if var_name in self.func_local_map:
                return self.func_local_map[var_name]["type"]
            return "i32"
        elif etype == "LiteralExpression":
            val = expr.get("value", 0)
            if isinstance(val, int):
                if -2**31 <= val <= 2**31 - 1:
                    return "i32"
                else:
                    return "i64"
            elif isinstance(val, float):
                return "f32"
            else:
                return "i32"
        return "i32"


@pytest.mark.parametrize("var_name,expr_node,declared_type,expected_lines", [
    # 1) Simple i32 assignment
    (
        "x",
        {"type": "LiteralExpression", "value": 42},
        "i32",
        [
            "  i32.const 42",
            "  local.set $x",
        ],
    ),
    # 2) Larger int => i64 => declare as i64
    (
        "bigVal",
        {"type": "LiteralExpression", "value": 2147483648},  # i64
        "i64",
        [
            "  i64.const 2147483648",
            "  local.set $bigVal",
        ],
    ),
    # 3) Float => f32 => declare as f32
    (
        "ratio",
        {"type": "LiteralExpression", "value": 3.14},  # f32
        "f32",
        [
            "  i32.const 3.14",     # mock emitter always does i32.const <val> for floats
            "  local.set $ratio",
        ],
    ),
    # 4) Variable => i32 => assign from variable expression => i32.const 999
    (
        "dest",
        {"type": "VariableExpression", "name": "source"},
        "i32",
        [
            "  i32.const 999",
            "  local.set $dest",
        ],
    ),
    # 5) No expression => fallback zero => i32 => declare as i32
    (
        "noExpr",
        None,
        "i32",
        [
            "  i32.const 0",
            "  local.set $noExpr",
        ],
    ),
])
def test_assignment_statement(var_name, expr_node, declared_type, expected_lines):
    """
    Tests that AssignmentEmitter emits the correct lines for a variety of
    expression scenarios, with each variable pre-declared to match the final type.
    """
    controller = MockController()
    emitter = AssignmentEmitter(controller)

    # Pre-declare the variable with declared_type, so no unify error
    name_in_map = controller._normalize_local_name(var_name)
    controller.func_local_map[name_in_map] = {
        "index": 0,
        "type": declared_type,
    }

    # Build the AST for the assignment
    node = {
        "type": "AssignmentStatement",
        "variable_name": var_name,
        "expression": expr_node,
    }

    out = []
    emitter.emit_assignment(node, out)

    combined = "\n".join(out)

    # Check lines
    for line in expected_lines:
        assert line in combined, f"Expected line '{line}' in:\n{combined}"


def test_assignment_existing_variable():
    """
    Example: A previously declared i64 variable, assigned a large int => i64
    """
    controller = MockController()
    # i64 from the start
    controller.func_local_map["$myVar"] = {"index": 0, "type": "i64"}

    emitter = AssignmentEmitter(controller)

    node = {
        "type": "AssignmentStatement",
        "variable_name": "myVar",
        "expression": {
            "type": "LiteralExpression",
            "value": 999999999999,  # large => i64
        },
    }

    out = []
    emitter.emit_assignment(node, out)
    combined = "\n".join(out)

    assert "  i64.const 999999999999" in combined
    assert "local.set $myVar" in combined

    # The variable remains i64
    info = controller.func_local_map["$myVar"]
    assert info["type"] == "i64"

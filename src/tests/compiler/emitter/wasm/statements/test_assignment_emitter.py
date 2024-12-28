# tests/emitter/wasm/statements/test_assignment_emitter.py

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
          - int literal => i32.const or i64.const
          - float => i32.const <val>
        """
        etype = expr.get("type") if expr else None
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
        Naive approach:
          - If it's a variable expression and we've declared it, return that type
          - If it's an int, choose i32 or i64
          - If it's a float, choose f32
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


@pytest.mark.parametrize("var_name, expr_node, declared_type, expected_lines", [
    # 1) Simple i32 assignment
    (
        "x",
        {"type": "LiteralExpression", "value": 42},
        "i32",   # declare x as i32
        [
            "  i32.const 42",
            "  local.set $x",
        ],
    ),
    # 2) Larger int => i64 => so declare bigVal as i64
    (
        "bigVal",
        {"type": "LiteralExpression", "value": 2147483648},  # just over i32 max
        "i64",
        [
            "  i64.const 2147483648",
            "  local.set $bigVal",
        ],
    ),
    # 3) Float => f32 => declare ratio as f32
    (
        "ratio",
        {"type": "LiteralExpression", "value": 3.14},
        "f32",
        [
            "  i32.const 3.14",  # Our naive mock emitter uses i32.const <float> 
            "  local.set $ratio",
        ],
    ),
    # 4) Variable => pretend i32.const 999 => declare 'dest' as i32
    (
        "dest",
        {"type": "VariableExpression", "name": "source"},
        "i32",
        [
            "  i32.const 999",
            "  local.set $dest",
        ],
    ),
    # 5) No expression => fallback zero => i32 => declare noExpr as i32
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

    # STEP 1) Pre-declare the variable in controller.func_local_map with declared_type
    declared_name = controller._normalize_local_name(var_name)
    controller.func_local_map[declared_name] = {
        "index": 0,
        "type": declared_type,
    }

    # STEP 2) Build the AST for an assignment
    node = {
        "type": "AssignmentStatement",
        "variable_name": var_name,
        "expression": expr_node,
    }

    # STEP 3) Emit
    out = []
    emitter.emit_assignment(node, out)

    combined = "\n".join(out)

    # STEP 4) Check lines
    for line in expected_lines:
        assert line in combined, f"Expected line '{line}' in output:\n{combined}"


def test_assignment_existing_variable():
    """
    Example of how you might test a variable declared as i64 from the start,
    then unify it with a large int expression to remain i64.
    """
    controller = MockController()
    # Pre-declare var 'myVar' as i64
    controller.func_local_map["$myVar"] = {
        "index": 0,
        "type": "i64",
    }

    emitter = AssignmentEmitter(controller)

    node = {
        "type": "AssignmentStatement",
        "variable_name": "myVar",
        "expression": {
            "type": "LiteralExpression",
            "value": 123456789123  # large => i64
        },
    }
    out = []
    emitter.emit_assignment(node, out)
    combined = "\n".join(out)

    # We expect i64.const because it's a large int
    assert "i64.const 123456789123" in combined
    # final set => local.set $myVar
    assert "local.set $myVar" in combined

    # Also ensure the symbol table remains "i64"
    final_info = controller.func_local_map["$myVar"]
    assert final_info["type"] == "i64"

# file: tests/compiler/emitter/test_binary_expression_emitter.py

import pytest
from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter

class MockController:
    """
    Mocks the Emitter's controller for expression emission.
    We'll produce a single line per expression, e.g. "i32.const 777",
    based on the expression's 'inferred_type'.
    """
    def __init__(self):
        self.emit_count = 0

    def emit_expression(self, expr, out_lines):
        """
        Fake emission for sub-expression 'expr'.
        We look at expr["inferred_type"] and produce "i32.const 777" or similar.

        This way, we can test how BinaryExpressionEmitter merges them.
        """
        inferred_t = expr.get("inferred_type", "i32")
        self.emit_count += 1

        if inferred_t == "i32":
            out_lines.append("  i32.const 777")
        elif inferred_t == "i64":
            out_lines.append("  i64.const 777")
        elif inferred_t == "f32":
            out_lines.append("  f32.const 777")
        elif inferred_t == "f64":
            out_lines.append("  f64.const 777")
        else:
            raise ValueError(f"Unknown inferred type: {inferred_t}")

OPERATOR_MAP = {
    "+":  {"i32": "i32.add",  "i64": "i64.add",  "f32": "f32.add",  "f64": "f64.add"},
    "-":  {"i32": "i32.sub",  "i64": "i64.sub",  "f32": "f32.sub",  "f64": "f64.sub"},
    "*":  {"i32": "i32.mul",  "i64": "i64.mul",  "f32": "f32.mul",  "f64": "f64.mul"},
    "/":  {"i32": "i32.div_s","i64": "i64.div_s","f32": "f32.div",  "f64": "f64.div"},
    "<":  {"i32": "i32.lt_s", "i64": "i64.lt_s", "f32": "f32.lt",   "f64": "f64.lt"},
    "<=": {"i32": "i32.le_s", "i64": "i64.le_s", "f32": "f32.le",   "f64": "f64.le"},
    ">":  {"i32": "i32.gt_s", "i64": "i64.gt_s", "f32": "f32.gt",   "f64": "f64.gt"},
    ">=": {"i32": "i32.ge_s", "i64": "i64.ge_s", "f32": "f32.ge",   "f64": "f64.ge"},
    "==": {"i32": "i32.eq",   "i64": "i64.eq",   "f32": "f32.eq",   "f64": "f64.eq"},
    "!=": {"i32": "i32.ne",   "i64": "i64.ne",   "f32": "f32.ne",   "f64": "f64.ne"},
}

def unify_types(t1, t2):
    """
    For the test, we define a simple priority-based unify:
      i32 < i64 < f32 < f64
    """
    priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
    return t1 if priority[t1] >= priority[t2] else t2

ALL_OPERATORS = list(OPERATOR_MAP.keys())  # +, -, etc.

ALL_TYPE_PAIRS = [
    ("i32", "i32"),
    ("i64", "i64"),
    ("f32", "f32"),
    ("f64", "f64"),
    ("i32", "i64"),  # unify => i64
    ("i32", "f32"),  # unify => f32
    ("i32", "f64"),  # unify => f64
    ("i64", "f32"),  # unify => f32
    ("i64", "f64"),  # unify => f64
    ("f32", "f64"),  # unify => f64
]

@pytest.mark.parametrize("op", ALL_OPERATORS)
@pytest.mark.parametrize("left_t,right_t", ALL_TYPE_PAIRS)
def test_binary_all_ops(left_t, right_t, op):
    """
    For each operator (+, -, /, etc.) and each pair of operand types,
    we unify to get a final type. Then we build a node with 'inferred_type' = final_type,
    and check if the emitter produces the correct WASM op.

    We also confirm it emitted the sub-expressions e.g. 'i32.const 777' lines for each side.
    """
    controller = MockController()
    be = BinaryExpressionEmitter(controller)

    final_type = unify_types(left_t, right_t)

    node = {
        "type": "BinaryExpression",
        "operator": op,
        "inferred_type": final_type,
        "left": {
            "type": "LiteralExpression",
            "value": 1,
            "inferred_type": left_t
        },
        "right": {
            "type": "LiteralExpression",
            "value": 2,
            "inferred_type": right_t
        },
    }

    out_lines = []
    be.emit(node, out_lines)

    # Expect two lines for the sub-expressions + 1 line for the final op
    # e.g. ["  i32.const 777", "  i32.const 777", "  i32.add"]
    assert len(out_lines) == 3, f"Expected 3 lines, got {len(out_lines)} => {out_lines}"

    # Sub-expressions must be '  i32.const 777' or similar
    assert out_lines[0].strip().endswith("const 777"), "Left operand line mismatch"
    assert out_lines[1].strip().endswith("const 777"), "Right operand line mismatch"

    # The final op line
    last_line = out_lines[-1].strip()
    expected_op = OPERATOR_MAP[op][final_type]
    assert last_line == expected_op, (
        f"For operator={op}, left={left_t}, right={right_t}, expected '{expected_op}' "
        f"but got '{last_line}'\nFull out: {out_lines}"
    )

@pytest.mark.parametrize("left_t,right_t", [
    ("i32", "i32"),
    ("f64", "i32"),
    ("f32", "f64"),
])
def test_binary_fallback(left_t, right_t):
    """
    Tests the fallback path for unknown operators => "<final_type>.add".
    """
    controller = MockController()
    be = BinaryExpressionEmitter(controller)

    final_type = unify_types(left_t, right_t)

    node = {
        "type": "BinaryExpression",
        "operator": "&",  # not recognized => fallback
        "inferred_type": final_type,
        "left":  {
            "type": "LiteralExpression",
            "value": 1,
            "inferred_type": left_t
        },
        "right": {
            "type": "LiteralExpression",
            "value": 2,
            "inferred_type": right_t
        },
    }
    out_lines = []
    be.emit(node, out_lines)

    assert out_lines[-1].strip() == f"{final_type}.add", (
        f"Fallback => expecting '{final_type}.add', got '{out_lines[-1].strip()}'\n{out_lines}"
    )

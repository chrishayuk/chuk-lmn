import pytest
from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter

#
# 1) A universal MockController that now just emits a single line per operand
#    but does NOT unify or infer type. We'll do that in the test's node creation.
#

class MockController:
    def __init__(self):
        self.emit_count = 0

    def emit_expression(self, expr, out_lines):
        """
        We simply look at expr["inferred_type"] to decide which const to emit.
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

#
# 2) A helper dict that indicates the expected final Wasm opcode
#    for each operator + final type, matching your _map_operator() logic.
#

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

#
# 3) We'll define a small function to unify types *just for the test*, to verify final lines.
#

def unify_types(t1, t2):
    priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
    return t1 if priority[t1] >= priority[t2] else t2

#
# 4) The set of operators and type pairs to test.
#

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

#
# 5) Parametrize over operator + (left_type, right_type).
#    We'll manually store 'inferred_type' in the AST node
#    so the emitter doesn't need to unify again.
#

@pytest.mark.parametrize("op", ALL_OPERATORS)
@pytest.mark.parametrize("left_t,right_t", ALL_TYPE_PAIRS)
def test_binary_all_ops(left_t, right_t, op):
    # 1) Create the emitter with a basic controller
    from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
    controller = MockController()
    be = BinaryExpressionEmitter(controller)

    # 2) Determine final type by unifying left_t, right_t
    final_type = unify_types(left_t, right_t)

    # 3) Build a node that ALREADY has 'inferred_type' => final_type
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

    out = []
    be.emit(node, out)

    # The last line in out is the final Wasm op
    last_line = out[-1].strip()

    # The opcode we expect
    expected_op = OPERATOR_MAP[op][final_type]

    assert last_line == expected_op, (
        f"For operator={op}, left={left_t}, right={right_t}, expected '{expected_op}' "
        f"but got '{last_line}'\nFull out: {out}"
    )


#
# 6) Test the fallback case (unknown operator => 'op_type.add')
#

@pytest.mark.parametrize("left_t,right_t", [("i32", "i32"), ("f64", "i32"), ("f32", "f64")])
def test_binary_fallback(left_t, right_t):
    from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
    controller = MockController()
    be = BinaryExpressionEmitter(controller)

    final_type = unify_types(left_t, right_t)

    node = {
        "type": "BinaryExpression",
        "operator": "&",  # not recognized
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
    out = []
    be.emit(node, out)

    assert out[-1].strip() == f"{final_type}.add", (
        f"Fallback => expecting '{final_type}.add', got '{out[-1].strip()}'\n{out}"
    )

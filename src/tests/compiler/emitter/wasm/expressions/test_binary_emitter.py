import pytest
from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter

#
# 1) A universal MockController that can return different types for left/right.
#    - By default, it can unify the first call to 'emit_expression'/'infer_type'
#      as the 'left_type' and the second call as the 'right_type'.
#    - This lets us parametrize and test i32, i64, f32, f64, plus mixes.
#

class MockController:
    def __init__(self, left_type="i32", right_type="i32"):
        self.left_type = left_type
        self.right_type = right_type
        self.emit_count = 0
        self.infer_count = 0

    def emit_expression(self, expr, out_lines):
        """
        First call => left_type.const 777
        Second call => right_type.const 777
        """
        if self.emit_count == 0:
            t = self.left_type
        else:
            t = self.right_type
        self.emit_count += 1

        if t == "i32":
            out_lines.append("  i32.const 777")
        elif t == "i64":
            out_lines.append("  i64.const 777")
        elif t == "f32":
            out_lines.append("  f32.const 777")
        elif t == "f64":
            out_lines.append("  f64.const 777")
        else:
            raise ValueError(f"Unknown mock type: {t}")

    def infer_type(self, expr):
        """
        Similarly, first call => left_type, second => right_type.
        """
        if self.infer_count == 0:
            self.infer_count += 1
            return self.left_type
        else:
            self.infer_count += 1
            return self.right_type


#
# 2) We'll define a helper dict that indicates the expected final Wasm opcode
#    for each operator + final type, matching your _map_operator() logic.
#    Then we'll unify the left/right to figure out the final type, and compare.
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
# 3) We'll define a small function to unify types like your emitter does:
#      i32 < i64 < f32 < f64
#

def unify_types(t1, t2):
    priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
    # return the higher
    return t1 if priority[t1] >= priority[t2] else t2


#
# 4) We'll gather all operators that your emitter recognizes, plus a "fallback" op.
#    For each operator, we test multiple type pairs:
#      (i32,i32), (i64,i64), (f32,f32), (f64,f64),
#      plus a few mixes: (i32,f64), (f32,i64), etc.
#

ALL_OPERATORS = list(OPERATOR_MAP.keys())  # +, -, *, /, <, <=, >, >=, ==, !=
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
# 5) Parametrize operator + (left_type,right_type). We'll check the final line.
#
@pytest.mark.parametrize("op", ALL_OPERATORS)
@pytest.mark.parametrize("left_t,right_t", ALL_TYPE_PAIRS)
def test_binary_all_ops(left_t, right_t, op):
    from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter

    # 1) Build the emitter with the mock
    controller = MockController(left_t, right_t)
    be = BinaryExpressionEmitter(controller)

    # 2) Create a sample node
    node = {
        "type": "BinaryExpression",
        "operator": op,
        "left":  {"type": "LiteralExpression", "value": 1},
        "right": {"type": "LiteralExpression", "value": 2},
    }

    out = []
    be.emit(node, out)

    # 3) The last line in out should be the final op.
    last_line = out[-1].strip()

    # 4) Determine the "unified" type => expected Wasm opcode from OPERATOR_MAP
    final_type = unify_types(left_t, right_t)
    expected_op = OPERATOR_MAP[op][final_type]

    # 5) Compare
    assert last_line == expected_op, (
        f"Operator '{op}' with left={left_t} and right={right_t} should produce '{expected_op}', "
        f"but got '{last_line}'.\nFull out={out}"
    )


#
# 6) Finally, test the fallback case: an unknown operator, e.g. "&"
#

@pytest.mark.parametrize("left_t,right_t", [("i32", "i32"), ("f64", "i32"), ("f32", "f64")])
def test_binary_fallback(left_t, right_t):
    """
    If we pass in an unknown operator, the emitter does 'op_type.add' as fallback.
    For i32 => i32.add, i64 => i64.add, f32 => f32.add, f64 => f64.add.
    """
    from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
    controller = MockController(left_t, right_t)
    be = BinaryExpressionEmitter(controller)

    node = {
        "type": "BinaryExpression",
        "operator": "&",  # not recognized in the map
        "left":  {"type": "LiteralExpression", "value": 1},
        "right": {"type": "LiteralExpression", "value": 2},
    }
    out = []
    be.emit(node, out)

    # The last line should be "i32.add" or "i64.add" or "f32.add" or "f64.add"
    final_type = unify_types(left_t, right_t)
    expected = f"{final_type}.add"
    assert out[-1].strip() == expected, (
        f"Fallback operator => expecting {expected}, got {out[-1].strip()}"
    )

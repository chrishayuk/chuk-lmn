# file: tests/compiler/emitter/test_assignment_expression_emitter.py

import pytest
from lmn.compiler.emitter.wasm.expressions.assignment_expression_emitter import AssignmentExpressionEmitter

class MockController:
    """
    A mock for your main WasmEmitter (or 'controller').
    We define:
      - unify_types(t1, t2, for_assignment=True) if needed
      - infer_type(expr)
      - emit_expression(expr, out_lines)
      - a local map to store variable types, etc. if you want
    """

    def __init__(self, var_map=None):
        """
        var_map: dictionary mapping var_name -> type (e.g. {"a":"i32","b":"i64"}).
        This helps us unify and see how we treat assignments.
        """
        self.var_map = var_map or {}

    def unify_types(self, t1, t2, for_assignment=False):
        """
        Minimal numeric hierarchy example: i32 < i64 < f32 < f64.
        If 'for_assignment' is True, we might pick the 'larger' type or do some rule.
        Adjust as your language requires.
        """
        priority = {"i32":1, "i64":2, "f32":3, "f64":4}
        if t1 == t2:
            return t1
        # if for_assignment => we might prefer the 'larger' type for the variable
        # or do something else. For simplicity:
        return t1 if priority[t1]>=priority[t2] else t2

    def emit_expression(self, expr, out_lines):
        """
        For the RHS or anything else. We'll do a minimal approach:
          - If it's a LiteralExpression => i32.const or i64.const ...
          - If it's a VariableExpression => local.get ...
          - If it's a BinaryExpression => "fake lines..."
          - etc.
        """
        etype = expr["type"]
        if etype == "LiteralExpression":
            expr_type = expr.get("inferred_type","i32")
            val = expr["value"]
            if expr_type == "i64":
                out_lines.append(f"  i64.const {val}")
            elif expr_type == "f32":
                out_lines.append(f"  f32.const {val}")
            elif expr_type == "f64":
                out_lines.append(f"  f64.const {val}")
            else: # default i32
                out_lines.append(f"  i32.const {val}")
        elif etype == "VariableExpression":
            var_name = expr["name"]
            normalized = self._normalize_local_name(var_name)
            out_lines.append(f"  local.get {normalized}")
        else:
            out_lines.append("  ;; [Mocked sub-expression emission]")

    def infer_type(self, expr):
        """
        If your emitter calls 'infer_type' on the RHS or similar,
        we can do something minimal:
          - if expr has 'inferred_type', use it
          - if it's a variable => look in var_map
          - else default "i32"
        """
        etype = expr["type"]
        if "inferred_type" in expr:
            return expr["inferred_type"]
        elif etype == "VariableExpression":
            var_name = expr["name"]
            return self.var_map.get(var_name,"i32")
        else:
            return "i32"

    def _normalize_local_name(self, var_name):
        """
        If your emitter normalizes e.g. 'x' => '$x', '$$thing' => '$thing', etc.
        We'll do a simple approach: if var_name doesn't start with '$', prepend it.
        """
        if var_name.startswith('$'):
            return var_name
        return f'${var_name}'


@pytest.mark.parametrize("var_type,rhs_type,final_type", [
    ("i32", "i32", "i32"),
    ("i32", "i64", "i64"),  # if unify => i64 overshadow i32
    ("i64", "i32", "i64"),
    ("f32", "f64", "f64"),
    ("i32", "f32", "f32"),
    ("i64", "f64", "f64"),
])
def test_simple_assignment(var_type, rhs_type, final_type):
    """
    Basic test: 'a = <some expr>' => 
      1) unify types if needed, 
      2) emit the RHS, 
      3) local.set $a, 
      4) optionally push the new value (C-like assignment yields a value).
    We'll check that:
      - we see lines for the sub-expression
      - we see local.set $a
      - we might see local.get $a if we want the assignment expr to yield a value
        (adapt if your language doesn't do that).
    """
    # Suppose we have var a declared as var_type in our mock
    controller = MockController(var_map={"a": var_type})
    emitter = AssignmentExpressionEmitter(controller)

    # Example node: a = literal(10)
    node = {
        "type": "AssignmentExpression",
        "left": {
            "type": "VariableExpression",
            "name": "a"
        },
        "right": {
            "type": "LiteralExpression",
            "value": 10,
            "inferred_type": rhs_type
        },
        # 'inferred_type': final_type  # if your code sets it on the assignment node
    }

    out_lines = []
    emitter.emit(node, out_lines)
    combined = "\n".join(out_lines)
    # We expect something like:
    #   i64.const 10   (if the RHS was i64)
    #   local.set $a
    #   local.get $a   (if returning the new value)
    # or some variant.

    # Check sub-expression line
    if rhs_type.startswith("i"):
        # i32 or i64 => e.g. "i64.const 10"
        assert f"{rhs_type}.const 10" in combined or f"i32.const 10" in combined, \
            f"expected {rhs_type}.const 10 in:\n{combined}"
    elif rhs_type.startswith("f"):
        # f32 or f64 => e.g. "f32.const 10" or "f64.const 10"
        assert f"{rhs_type}.const 10" in combined, \
            f"expected {rhs_type}.const 10 in:\n{combined}"

    # Check local.set $a
    assert "local.set $a" in combined, f"Expected local.set $a in:\n{combined}"

    # If your language sees assignment expressions as yielding the new value:
    # the emitter might do local.get $a afterwards. If not, remove this check.
    if True:  # or some condition
        # typical C-like: a = expr => push new a on stack
        assert "local.get $a" in combined or "local.get $a" in out_lines[-1], (
            f"Expected to push new value 'local.get $a' at the end:\n{combined}"
        )


def test_assignment_nonvar_lhs():
    """
    Suppose an assignment node must have a 'VariableExpression' on LHS.
    If your emitter checks that, we test the error or fallback logic.
    """
    controller = MockController({"x":"i32"})
    emitter = AssignmentExpressionEmitter(controller)
    node = {
        "type": "AssignmentExpression",
        "left": {
            "type": "LiteralExpression",  # not a var => error
            "value": 999
        },
        "right": {
            "type": "LiteralExpression",
            "value": 10,
            "inferred_type":"i32"
        }
    }
    out_lines = []
    # we might expect a TypeError or a fallback. We'll do:
    with pytest.raises(TypeError, match="AssignmentExpression LHS must be a variable, got LiteralExpression"):
        emitter.emit(node, out_lines)


def test_assignment_synthesized_var():
    """
    If the LHS variable wasn't in var_map, we might do a new declaration 
    or default it to i32. Depends on your design. We'll see how it behaves.
    """
    controller = MockController(var_map={})
    emitter = AssignmentExpressionEmitter(controller)
    node = {
        "type": "AssignmentExpression",
        "left": {
            "type": "VariableExpression",
            "name": "newVar"
        },
        "right": {
            "type": "LiteralExpression",
            "value": 77,
            "inferred_type":"i32"
        }
    }
    out_lines = []
    emitter.emit(node, out_lines)
    combined = "\n".join(out_lines)
    # We expect "i32.const 77" then "local.set $newVar" maybe.
    assert "i32.const 77" in combined, f"Did not see i32.const 77:\n{combined}"
    assert "local.set $newVar" in combined, f"Expected local.set for newVar:\n{combined}"


@pytest.mark.skip(reason="If your assignment emitter also handles compound =, e.g. a+=3, test here.")
def test_compound_assignment():
    pass

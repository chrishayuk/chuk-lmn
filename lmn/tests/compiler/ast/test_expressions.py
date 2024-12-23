# tests/test_expressions.py
# Instead of importing from submodules like 'literal_expression.py', etc.,
# we import them from the single 'compiler.ast' package, which references the mega-union classes.
from compiler.ast import (
    LiteralExpression,
    BinaryExpression,
    UnaryExpression,
    FnExpression,
    VariableExpression,
)


def test_literal_int():
    lit = LiteralExpression(value="5")
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    assert d["value"] == 5  # int
    assert str(lit) == "5"


def test_literal_float():
    lit = LiteralExpression(value="3.14")
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    assert d["value"] == 3.14
    assert str(lit) == "3.14"


def test_literal_string():
    lit = LiteralExpression(value="hello")
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    assert d["value"] == "hello"
    assert str(lit) == "hello"


def test_binary_expression():
    left = LiteralExpression(value="5")
    right = LiteralExpression(value="3")
    expr = BinaryExpression(operator="+", left=left, right=right)

    d = expr.to_dict()
    assert d["type"] == "BinaryExpression"
    assert d["operator"] == "+"
    # sub-fields fully expanded
    assert d["left"]["type"] == "LiteralExpression"
    assert d["left"]["value"] == 5
    assert d["right"]["type"] == "LiteralExpression"
    assert d["right"]["value"] == 3

    s = str(expr)
    assert "+" in s
    assert "5" in s
    assert "3" in s


def test_unary_expression():
    operand = LiteralExpression(value="10")
    expr = UnaryExpression(operator="-", operand=operand)

    d = expr.to_dict()
    assert d["type"] == "UnaryExpression"
    assert d["operator"] == "-"
    assert d["operand"]["type"] == "LiteralExpression"
    assert d["operand"]["value"] == 10

    s = str(expr)
    assert "-" in s
    assert "10" in s


def test_fn_expression_single_arg():
    name = VariableExpression(name="fact")
    arg = LiteralExpression(value="5")
    expr = FnExpression(name=name, arguments=[arg])

    d = expr.to_dict()
    assert d["type"] == "FnExpression"
    assert d["name"]["type"] == "VariableExpression"
    assert d["name"]["name"] == "fact"

    assert len(d["arguments"]) == 1
    assert d["arguments"][0]["type"] == "LiteralExpression"
    assert d["arguments"][0]["value"] == 5

    s = str(expr)
    assert "fact" in s
    assert "5" in s


def test_fn_expression_multiple_args():
    name = VariableExpression(name="sum")
    arg1 = VariableExpression(name="a")
    arg2 = VariableExpression(name="b")
    arg3 = LiteralExpression(value="10")

    expr = FnExpression(name=name, arguments=[arg1, arg2, arg3])
    d = expr.to_dict()

    assert d["type"] == "FnExpression"
    assert d["name"]["type"] == "VariableExpression"
    assert d["name"]["name"] == "sum"

    assert len(d["arguments"]) == 3
    assert d["arguments"][0]["type"] == "VariableExpression"
    assert d["arguments"][0]["name"] == "a"
    assert d["arguments"][1]["type"] == "VariableExpression"
    assert d["arguments"][1]["name"] == "b"
    assert d["arguments"][2]["type"] == "LiteralExpression"
    assert d["arguments"][2]["value"] == 10

    s = str(expr)
    assert "sum" in s
    assert "a" in s
    assert "b" in s
    assert "10" in s

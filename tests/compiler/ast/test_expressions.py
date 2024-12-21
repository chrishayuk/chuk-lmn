# tests/test_expressions.py
from compiler.ast.expressions.literal import Literal
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.expressions.unary_expression import UnaryExpression
from compiler.ast.expressions.fn_expression import FnExpression
from compiler.ast.variable import Variable
from compiler.lexer.token_type import LmnTokenType

def test_literal_int():
    lit = Literal("5")  # Will parse as Decimal(5)
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    assert d["value"] == 5  # int
    assert str(lit) == "5"

def test_literal_float():
    lit = Literal("3.14")
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    assert d["value"] == 3.14  # float
    assert str(lit) == "3.14"

def test_literal_string():
    lit = Literal("hello")
    d = lit.to_dict()
    assert d["type"] == "LiteralExpression"
    # Because "hello" is not numeric, we store it as a string
    assert d["value"] == "hello"
    assert str(lit) == "hello"

def test_binary_expression():
    left = Literal("5")
    right = Literal("3")
    op = LmnTokenType.PLUS  # e.g. plus operator
    
    expr = BinaryExpression(left, op, right)
    d = expr.to_dict()

    assert d["type"] == "BinaryExpression"
    assert d["operator"] == "+"  # from op.value if op = LmnTokenType.PLUS
    assert d["left"]["value"] == 5
    assert d["right"]["value"] == 3

    # Check the string representation
    s = str(expr)
    # Should look like "(5 + 3)" or "5 + 3" depending on your __str__ implementation
    assert "+" in s

def test_unary_expression():
    operand = Literal("10")
    op = LmnTokenType.MINUS  # e.g. unary minus
    
    expr = UnaryExpression(op, operand)
    d = expr.to_dict()

    assert d["type"] == "UnaryExpression"
    assert d["operator"] == "-"
    assert d["operand"]["value"] == 10

    # Check str
    assert "-" in str(expr)

def test_fn_expression_single_arg():
    # e.g. fact(5)
    name = Variable("fact")
    arg = Literal("5")
    expr = FnExpression(name, [arg])

    d = expr.to_dict()
    assert d["type"] == "FnExpression"
    # name should be a dict of type "Variable"
    assert d["name"]["type"] == "Variable"
    assert d["name"]["name"] == "fact"

    assert len(d["arguments"]) == 1
    assert d["arguments"][0]["type"] == "LiteralExpression"
    assert d["arguments"][0]["value"] == 5

    # Check str
    s = str(expr)
    # Should be something like "fact(5)"
    assert "fact" in s
    assert "5" in s

def test_fn_expression_multiple_args():
    # sum(a, b, 10)
    name = Variable("sum")
    arg1 = Variable("a")
    arg2 = Variable("b")
    arg3 = Literal("10")

    expr = FnExpression(name, [arg1, arg2, arg3])
    d = expr.to_dict()

    assert d["type"] == "FnExpression"
    assert d["name"]["name"] == "sum"
    assert len(d["arguments"]) == 3
    # arguments can be variable or literal
    assert d["arguments"][0]["type"] == "Variable"
    assert d["arguments"][1]["type"] == "Variable"
    assert d["arguments"][2]["value"] == 10

    # Check str
    s = str(expr)
    assert "sum" in s
    assert "a" in s
    assert "b" in s
    assert "10" in s

# tests/test_statements.py
import pytest

# Import statement classes
from compiler.ast.statements.if_statement import IfStatement
from compiler.ast.statements.set_statement import SetStatement
from compiler.ast.statements.print_statement import PrintStatement
from compiler.ast.statements.return_statement import ReturnStatement
from compiler.ast.statements.for_statement import ForStatement

# If you have a call statement:
# from compiler.ast.statements.call_statement import CallStatement

# Import expression and variable helpers
from compiler.ast.expressions.literal import Literal
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.variable import Variable

def test_if_statement_no_else():
    # condition: x < 10
    cond = BinaryExpression(Variable("x"), "<", Literal("10"))
    
    # then body: set x 5
    then_body = SetStatement(Variable("x"), Literal("5"))
    
    stmt = IfStatement(cond, then_body, else_body=None)
    d = stmt.to_dict()

    assert d["type"] == "IfStatement"
    # condition check
    assert d["condition"]["type"] == "BinaryExpression"
    assert d["condition"]["operator"] == "<"
    # thenBody is a list with one statement
    assert len(d["thenBody"]) == 1
    assert d["thenBody"][0]["type"] == "SetStatement"
    # elseBody is empty
    assert len(d["elseBody"]) == 0

    # Check string
    s = str(stmt)
    assert "if" in s
    assert "<" in s
    assert "set" in s

def test_if_statement_with_else():
    # condition: n <= 1
    cond = BinaryExpression(Variable("n"), "<=", Literal("1"))
    # then body: return 1
    then_body = ReturnStatement(Literal("1"))
    # else body: print "bigger"
    else_body = PrintStatement([Literal("bigger")])

    stmt = IfStatement(cond, then_body, else_body)
    d = stmt.to_dict()

    assert d["type"] == "IfStatement"
    assert len(d["thenBody"]) == 1
    assert len(d["elseBody"]) == 1
    # Verify else is PrintStatement
    assert d["elseBody"][0]["type"] == "PrintStatement"

def test_set_statement():
    # set x 10
    var = Variable("x")
    expr = Literal("10")
    stmt = SetStatement(var, expr)
    
    d = stmt.to_dict()
    assert d["type"] == "SetStatement"
    assert d["variable"]["type"] == "Variable"
    assert d["variable"]["name"] == "x"
    assert d["expression"]["type"] == "LiteralExpression"
    assert d["expression"]["value"] == 10

    assert "set x =" in str(stmt)

def test_print_statement():
    # print "Hello" 42
    stmt = PrintStatement([Literal("Hello"), Literal("42")])
    d = stmt.to_dict()

    assert d["type"] == "PrintStatement"
    assert len(d["expressions"]) == 2
    assert d["expressions"][0]["value"] == "Hello"
    assert d["expressions"][1]["value"] == 42  # numeric parse

    s = str(stmt)
    assert "print" in s
    assert "Hello" in s
    assert "42" in s

def test_return_statement():
    # return n * 2
    expr = BinaryExpression(Variable("n"), "*", Literal("2"))
    stmt = ReturnStatement(expr)

    d = stmt.to_dict()
    assert d["type"] == "ReturnStatement"
    assert d["expression"]["type"] == "BinaryExpression"
    assert d["expression"]["operator"] == "*"

    s = str(stmt)
    assert "return" in s
    assert "*" in s

def test_for_statement_basic():
    # for i 1 to 5
    var = Variable("i")
    start_expr = Literal("1")
    end_expr = Literal("5")
    # body: print i
    body = [PrintStatement([Variable("i")])]

    stmt = ForStatement(var, start_expr, end_expr, None, body)
    d = stmt.to_dict()

    assert d["type"] == "ForStatement"
    assert d["variable"]["type"] == "Variable"
    assert d["variable"]["name"] == "i"
    assert d["start"]["type"] == "LiteralExpression"
    assert d["start"]["value"] == 1
    assert d["end"]["value"] == 5
    # step is None
    assert d["step"] is None

    # Body has 1 statement: print i
    assert len(d["body"]) == 1
    assert d["body"][0]["type"] == "PrintStatement"

    s = str(stmt)
    assert "for" in s
    assert "i" in s
    assert "1" in s
    assert "5" in s

# If you have a call statement:
# def test_call_statement():
#     # call "someTool" x 7
#     stmt = CallStatement("someTool", [Variable("x"), Literal("7")])
#     d = stmt.to_dict()
#     assert d["type"] == "CallStatement"
#     assert d["toolName"] == "someTool"
#     assert len(d["arguments"]) == 2
#     assert d["arguments"][0]["type"] == "Variable"
#     assert d["arguments"][1]["value"] == 7
#     
#     s = str(stmt)
#     assert 'call "someTool"' in s
#     assert 'x' in s
#     assert '7' in s

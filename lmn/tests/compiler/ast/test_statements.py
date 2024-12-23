# tests/test_statements.py

import pytest

# Instead of submodules, import from compiler.ast (the mega-union approach)
from compiler.ast import (
    IfStatement,
    SetStatement,
    PrintStatement,
    ReturnStatement,
    ForStatement,
    # CallStatement,  # Uncomment if you have a call statement test
    LiteralExpression,
    BinaryExpression,
    VariableExpression,
)

def test_if_statement_no_else():
    # condition: x < 10
    cond = BinaryExpression(
        operator="<",
        left=VariableExpression(name="x"),
        right=LiteralExpression(value="10")
    )
    
    # then body: set x 5
    then_body = SetStatement(
        variable=VariableExpression(name="x"),
        expression=LiteralExpression(value="5")
    )
    
    # IfStatement with a single item in then_body and empty else_body
    stmt = IfStatement(condition=cond, then_body=[then_body], else_body=[])

    # If your IfStatement’s to_dict() or model_dump() uses by_alias=True internally,
    # or you are calling .model_dump(by_alias=True) in your code:
    d = stmt.to_dict()  # or stmt.model_dump(by_alias=True)

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
    cond = BinaryExpression(
        operator="<=",
        left=VariableExpression(name="n"),
        right=LiteralExpression(value="1")
    )
    # then body: return 1
    then_body = ReturnStatement(
        expression=LiteralExpression(value="1")
    )
    # else body: print "bigger"
    else_body = PrintStatement(
        expressions=[LiteralExpression(value="bigger")]
    )

    stmt = IfStatement(condition=cond, then_body=[then_body], else_body=[else_body])
    d = stmt.to_dict()  # or stmt.model_dump(by_alias=True)

    assert d["type"] == "IfStatement"
    assert len(d["thenBody"]) == 1
    assert len(d["elseBody"]) == 1
    # Verify else is PrintStatement
    assert d["elseBody"][0]["type"] == "PrintStatement"

def test_set_statement():
    # set x 10
    stmt = SetStatement(
        variable=VariableExpression(name="x"),
        expression=LiteralExpression(value="10")
    )
    
    d = stmt.to_dict()
    assert d["type"] == "SetStatement"
    assert d["variable"]["type"] == "VariableExpression"
    assert d["variable"]["name"] == "x"
    assert d["expression"]["type"] == "LiteralExpression"
    assert d["expression"]["value"] == 10  # numeric parse

    assert "set x =" in str(stmt)

def test_print_statement():
    # print "Hello" 42
    stmt = PrintStatement(
        expressions=[
            LiteralExpression(value="Hello"),
            LiteralExpression(value="42")
        ]
    )
    d = stmt.to_dict()

    assert d["type"] == "PrintStatement"
    assert len(d["expressions"]) == 2
    assert d["expressions"][0]["type"] == "LiteralExpression"
    assert d["expressions"][0]["value"] == "Hello"
    # "42" => numeric parse => 42
    assert d["expressions"][1]["value"] == 42

    s = str(stmt)
    assert "print" in s
    assert "Hello" in s
    assert "42" in s

def test_return_statement():
    # return n * 2
    expr = BinaryExpression(
        operator="*",
        left=VariableExpression(name="n"),
        right=LiteralExpression(value="2")
    )
    stmt = ReturnStatement(expression=expr)

    d = stmt.to_dict()
    assert d["type"] == "ReturnStatement"
    assert d["expression"]["type"] == "BinaryExpression"
    assert d["expression"]["operator"] == "*"

    s = str(stmt)
    assert "return" in s
    assert "*" in s

def test_for_statement_basic():
    # for i 1 to 5
    stmt = ForStatement(
        variable=VariableExpression(name="i"),
        start_expr=LiteralExpression(value="1"),
        end_expr=LiteralExpression(value="5"),
        step_expr=None,
        body=[
            PrintStatement(expressions=[VariableExpression(name="i")])
        ]
    )
    d = stmt.to_dict()

    assert d["type"] == "ForStatement"
    # variable is a VariableExpression
    assert d["variable"]["type"] == "VariableExpression"
    assert d["variable"]["name"] == "i"
    # start_expr => "1"
    assert d["start_expr"]["type"] == "LiteralExpression"
    assert d["start_expr"]["value"] == 1
    # end_expr => "5"
    assert d["end_expr"]["value"] == 5
    # step_expr is None
    assert d["step_expr"] is None

    # Body has 1 statement: print i
    assert len(d["body"]) == 1
    assert d["body"][0]["type"] == "PrintStatement"

    s = str(stmt)
    assert "for" in s
    assert "i" in s
    assert "1" in s
    assert "5" in s

# If you have a call statement test:
# def test_call_statement():
#     # call "someTool" x 7
#     stmt = CallStatement(
#         tool_name="someTool",
#         arguments=[
#             VariableExpression(name="x"),
#             LiteralExpression(value="7")
#         ]
#     )
#     d = stmt.to_dict()
#     assert d["type"] == "CallStatement"
#     assert d["tool_name"] == "someTool"
#     assert len(d["arguments"]) == 2
#     assert d["arguments"][0]["type"] == "VariableExpression"
#     assert d["arguments"][1]["value"] == 7
#     
#     s = str(stmt)
#     assert 'call "someTool"' in s
#     assert 'x' in s
#     assert '7' in s

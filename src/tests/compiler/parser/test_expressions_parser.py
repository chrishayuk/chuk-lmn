# tests/test_expressions_parser.py
from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser
from lmn.compiler.ast import (
    LiteralExpression,
    BinaryExpression,
    VariableExpression,
    FnExpression,
    # etc.
)

def parse_single_expr(code: str):
    """Helper to parse a single expression from code that might only contain one statement."""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()
    # Suppose you store your expression as something like the first statement's expression,
    # or if your DSL allows code containing just an expression as a statement.
    # For a simpler approach, if your grammar allows an expression stand-alone, do:
    return program_ast.body[0].expression

def test_parse_literal_expr():
    code = "print 42"
    # We'll parse 'print 42' as a statement, then pull out the expression
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    stmt = program_ast.body[0]
    expr = stmt.expressions[0]
    assert isinstance(expr, LiteralExpression)
    assert expr.value == 42

def test_parse_binary_expr():
    code = "print x + 5"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    stmt = program_ast.body[0]
    expr = stmt.expressions[0]
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "+"

    left_dict = expr.left.model_dump(by_alias=True)
    right_dict = expr.right.model_dump(by_alias=True)

    assert left_dict["type"] == "VariableExpression"
    assert left_dict["name"] == "x"
    assert right_dict["type"] == "LiteralExpression"
    assert right_dict["value"] == 5

def test_parse_fn_expression():
    code = "print sum(a, b, 10)"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # The first statement is 'print sum(a, b, 10)'
    stmt = program_ast.body[0]
    fn_expr = stmt.expressions[0]
    assert isinstance(fn_expr, FnExpression)

    name_dict = fn_expr.name.model_dump(by_alias=True)
    assert name_dict["type"] == "VariableExpression"
    assert name_dict["name"] == "sum"

    assert len(fn_expr.arguments) == 3
    assert fn_expr.arguments[0].model_dump(by_alias=True)["name"] == "a"
    assert fn_expr.arguments[1].model_dump(by_alias=True)["name"] == "b"
    assert fn_expr.arguments[2].model_dump(by_alias=True)["value"] == 10

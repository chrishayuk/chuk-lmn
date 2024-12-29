# tests/test_expressions_parser.py

from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
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
    # If your DSL allows an expression alone as a statement, we can do:
    return program_ast.body[0].expression

#
# Basic tests
#

def test_parse_literal_expr():
    code = "print 42"
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

    stmt = program_ast.body[0]
    fn_expr = stmt.expressions[0]
    assert isinstance(fn_expr, FnExpression)

    name_dict = fn_expr.name.model_dump(by_alias=True)
    assert name_dict["type"] == "VariableExpression"
    assert name_dict["name"] == "sum"

    assert len(fn_expr.arguments) == 3
    # arg0 => a
    assert fn_expr.arguments[0].model_dump(by_alias=True)["name"] == "a"
    # arg1 => b
    assert fn_expr.arguments[1].model_dump(by_alias=True)["name"] == "b"
    # arg2 => 10
    assert fn_expr.arguments[2].model_dump(by_alias=True)["value"] == 10

#
# Extended Operators
#

def test_floor_div():
    code = "print a // b"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    stmt = program_ast.body[0]
    expr = stmt.expressions[0]
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "//"

def test_modulo_op():
    code = "print x % 10"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "%"

def test_postfix_increment():
    code = "print a++"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    assert isinstance(expr, PostfixExpression)
    assert expr.operator == "++"
    assert isinstance(expr.operand, VariableExpression)
    assert expr.operand.name == "a"

def test_postfix_decrement():
    code = "print b--"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    assert isinstance(expr, PostfixExpression)
    assert expr.operator == "--"
    assert isinstance(expr.operand, VariableExpression)
    assert expr.operand.name == "b"

def test_compound_assignment_plus_eq():
    code = "print a += 3"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    assert isinstance(expr, AssignmentExpression)
    # a += 3 => a = a + 3 in the AST
    left_var = expr.left
    right_expr = expr.right
    assert isinstance(left_var, VariableExpression)
    assert left_var.name == "a"

    assert isinstance(right_expr, BinaryExpression)
    assert right_expr.operator == "+"
    assert isinstance(right_expr.left, VariableExpression)
    assert right_expr.left.name == "a"
    assert isinstance(right_expr.right, LiteralExpression)
    assert right_expr.right.value == 3

def test_compound_assignment_eq_plus():
    code = "print a =+ 5"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    # a =+ 5 => a = a + 5
    assert isinstance(expr, AssignmentExpression)
    assert isinstance(expr.left, VariableExpression)
    assert expr.left.name == "a"
    assert isinstance(expr.right, BinaryExpression)
    assert expr.right.operator == "+"
    assert isinstance(expr.right.left, VariableExpression)
    assert expr.right.left.name == "a"
    assert isinstance(expr.right.right, LiteralExpression)
    assert expr.right.right.value == 5

def test_chain_assignment():
    code = "print x = y = 10"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    expr = program_ast.body[0].expressions[0]
    # If your language supports chaining, x = (y = 10)
    assert isinstance(expr, AssignmentExpression)
    # top-level => x on the left
    assert isinstance(expr.left, VariableExpression)
    assert expr.left.name == "x"
    # right => another assignment
    right_assign = expr.right
    assert isinstance(right_assign, AssignmentExpression)
    assert isinstance(right_assign.left, VariableExpression)
    assert right_assign.left.name == "y"
    assert isinstance(right_assign.right, LiteralExpression)
    assert right_assign.right.value == 10

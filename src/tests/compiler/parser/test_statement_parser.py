# tests/test_statements_parser.py
# Import the tokenizer, parser, and relevant AST nodes from your mega-union approach
from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser
from lmn.compiler.ast import (
    Program,
    IfStatement,
    SetStatement,
    PrintStatement,
    ReturnStatement,
    ForStatement,
    LiteralExpression,   # If your statements test needs to check some expression details
    VariableExpression,
)


def test_parse_empty():
    code = ""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect a Program node with an empty body
    assert isinstance(program_ast, Program)
    assert len(program_ast.body) == 0  # Or program_ast.statements if that's how you store them


def test_parse_set_statement():
    code = "set x 5"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, SetStatement)
    # Check the variable name
    assert stmt.variable.name == "x"
    # The expression should be a literal with value=5
    lit_dict = stmt.expression.model_dump(by_alias=True)
    assert lit_dict["type"] == "LiteralExpression"
    assert lit_dict["value"] == 5


def test_parse_print_statement():
    code = "print 10 20"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, PrintStatement)
    # We expect 2 expressions in the PrintStatement
    exprs = stmt.expressions
    assert len(exprs) == 2
    # Both should be LiteralExpression(10) and LiteralExpression(20)
    assert exprs[0].model_dump(by_alias=True)["value"] == 10
    assert exprs[1].model_dump(by_alias=True)["value"] == 20


def test_parse_if_no_else():
    code = """
    if (x < 10)
      print "Less"
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, IfStatement)
    # Condition should be a BinaryExpression with operator "<"
    cond_dict = stmt.condition.model_dump(by_alias=True)
    assert cond_dict["type"] == "BinaryExpression"
    assert cond_dict["operator"] == "<"
    # thenBody has 1 statement: print
    assert len(stmt.then_body) == 1
    assert isinstance(stmt.then_body[0], PrintStatement)
    # elseBody is empty
    assert len(stmt.else_body) == 0


def test_parse_if_with_else():
    code = """
    if (x >= 5)
      print "big"
    else
      print "small"
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, IfStatement)
    # Condition: x >= 5
    cond_dict = stmt.condition.model_dump(by_alias=True)
    assert cond_dict["operator"] == ">="
    # thenBody: [print "big"]
    assert len(stmt.then_body) == 1
    assert isinstance(stmt.then_body[0], PrintStatement)
    # elseBody: [print "small"]
    assert len(stmt.else_body) == 1
    assert isinstance(stmt.else_body[0], PrintStatement)


def test_parse_return_statement():
    code = "return x + 1"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, ReturnStatement)
    # expression is a binary expression x + 1
    expr_dict = stmt.expression.model_dump(by_alias=True)
    assert expr_dict["type"] == "BinaryExpression"
    assert expr_dict["operator"] == "+"


def test_parse_for_range():
    code = """
    for i 1 to 5
      print i
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, ForStatement)
    # ForStatement with variable i
    assert stmt.variable.name == "i"
    # start_expr=1, end_expr=5
    start_dict = stmt.start_expr.model_dump(by_alias=True)
    assert start_dict["value"] == 1
    end_dict = stmt.end_expr.model_dump(by_alias=True)
    assert end_dict["value"] == 5
    # step_expr is None
    assert stmt.step_expr is None
    # body has 1 statement: print i
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], PrintStatement)


def test_parse_for_in():
    code = """
    for city in locations
      print city
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, ForStatement)
    # variable = "city"
    assert stmt.variable.name == "city"
    # start_expr is "locations", end_expr=None
    loc_dict = stmt.start_expr.model_dump(by_alias=True)
    assert loc_dict["type"] == "VariableExpression"
    assert loc_dict["name"] == "locations"
    assert stmt.end_expr is None
    # body has 1 statement: print city
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], PrintStatement)


def test_parse_complex():
    code = """
    set x 3
    if (x < 5)
      x = x + 1
      print x
    else
      print "Done"
    end
    """
    # If your DSL expects "set x x + 1" rather than "x = x + 1", adjust as needed:
    code = code.replace("x = x + 1", "set x x + 1")

    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 2

    # 1) set x 3
    set_stmt = program_ast.body[0]
    assert isinstance(set_stmt, SetStatement)
    assert set_stmt.variable.name == "x"
    lit_dict = set_stmt.expression.model_dump(by_alias=True)
    assert lit_dict["value"] == 3

    # 2) if statement
    if_stmt = program_ast.body[1]
    assert isinstance(if_stmt, IfStatement)
    cond_dict = if_stmt.condition.model_dump(by_alias=True)
    assert cond_dict["operator"] == "<"
    # then body has 2 statements: set x x + 1, print x
    assert len(if_stmt.then_body) == 2
    then_set = if_stmt.then_body[0]
    assert isinstance(then_set, SetStatement)
    bin_expr_dict = then_set.expression.model_dump(by_alias=True)
    assert bin_expr_dict["type"] == "BinaryExpression"
    assert bin_expr_dict["operator"] == "+"
    assert bin_expr_dict["left"]["type"] == "VariableExpression"
    assert bin_expr_dict["left"]["name"] == "x"

    then_print = if_stmt.then_body[1]
    assert isinstance(then_print, PrintStatement)
    # else body has 1 statement: print "Done"
    assert len(if_stmt.else_body) == 1
    else_print = if_stmt.else_body[0]
    assert isinstance(else_print, PrintStatement)
    assert else_print.expressions[0].model_dump(by_alias=True)["value"] == "Done"

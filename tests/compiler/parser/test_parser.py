# tests/test_parser.py

from compiler.lexer.tokenizer import Tokenizer
from compiler.parser.parser import Parser
from compiler.ast.program import Program
from compiler.ast.statements.if_statement import IfStatement
from compiler.ast.statements.set_statement import SetStatement
from compiler.ast.statements.print_statement import PrintStatement
from compiler.ast.statements.return_statement import ReturnStatement
from compiler.ast.statements.for_statement import ForStatement
from compiler.ast.variable import Variable

def test_parse_empty():
    code = ""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect a Program node with an empty body
    assert isinstance(program_ast, Program)
    assert len(program_ast.statements) == 0

def test_parse_set_statement():
    code = "set x 5"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, SetStatement)
    # Check the variable name
    assert stmt.variable.name == "x"
    # The expression should be a literal with value=5
    lit_dict = stmt.expression.to_dict()
    assert lit_dict["type"] == "LiteralExpression"
    assert lit_dict["value"] == 5

def test_parse_print_statement():
    code = "print 10 20"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, PrintStatement)
    # We expect 2 expressions in the PrintStatement
    exprs = stmt.expressions
    assert len(exprs) == 2
    # Both should be Literal(10) and Literal(20)
    assert exprs[0].to_dict()["value"] == 10
    assert exprs[1].to_dict()["value"] == 20

def test_parse_if_no_else():
    code = """
    if (x < 10)
      print "Less"
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, IfStatement)
    # Condition should be a BinaryExpression with operator "<"
    cond_dict = stmt.condition.to_dict()
    assert cond_dict["type"] == "BinaryExpression"
    assert cond_dict["operator"] == "<"
    # then_body has 1 statement: print
    assert len(stmt.then_body) == 1
    assert isinstance(stmt.then_body[0], PrintStatement)
    # else_body is empty
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

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, IfStatement)
    # Condition: x >= 5
    cond_dict = stmt.condition.to_dict()
    assert cond_dict["operator"] == ">="
    # then_body: [print "big"]
    assert len(stmt.then_body) == 1
    assert isinstance(stmt.then_body[0], PrintStatement)
    # else_body: [print "small"]
    assert len(stmt.else_body) == 1
    assert isinstance(stmt.else_body[0], PrintStatement)

def test_parse_return_statement():
    code = "return x + 1"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, ReturnStatement)
    # expression is a binary expression x + 1
    expr_dict = stmt.expression.to_dict()
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

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, ForStatement)
    # ForStatement with variable i
    assert stmt.variable.name == "i"
    # start_expr=1, end_expr=5
    start_dict = stmt.start_expr.to_dict()
    assert start_dict["value"] == 1
    end_dict = stmt.end_expr.to_dict()
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

    assert len(program_ast.statements) == 1
    stmt = program_ast.statements[0]
    assert isinstance(stmt, ForStatement)
    # variable = "city"
    assert stmt.variable.name == "city"
    # start_expr is "locations", end_expr=None
    loc_dict = stmt.start_expr.to_dict()
    # If your variable references produce {"type": "Variable", "name": "locations"}, check accordingly
    assert loc_dict["type"] == "Variable"
    assert loc_dict["name"] == "locations"
    assert stmt.end_expr is None
    # body has 1 statement: print city
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], PrintStatement)

def test_parse_complex():
    code = """
    set x 3
    if (x < 5)
      x = x + 1  // or "set x x + 1" in LMN
      print x
    else
      print "Done"
    end
    """
    # Note: might need to adapt "x = x + 1" to your actual DSL "set x x + 1"
    # if you strictly require "set x expr".
    code = code.replace("x = x + 1", "set x x + 1")

    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 2

    # 1) set x 3
    set_stmt = program_ast.statements[0]
    assert isinstance(set_stmt, SetStatement)
    assert set_stmt.variable.name == "x"
    lit_dict = set_stmt.expression.to_dict()
    assert lit_dict["value"] == 3

    # 2) if statement
    if_stmt = program_ast.statements[1]
    assert isinstance(if_stmt, IfStatement)
    cond_dict = if_stmt.condition.to_dict()
    assert cond_dict["operator"] == "<"
    assert cond_dict["right"]["value"] == 5

    # then body has 2 statements: set x x + 1, print x
    assert len(if_stmt.then_body) == 2
    then_set = if_stmt.then_body[0]
    assert isinstance(then_set, SetStatement)
    # expression is a binary expression "x + 1"
    bin_expr_dict = then_set.expression.to_dict()
    assert bin_expr_dict["type"] == "BinaryExpression"
    assert bin_expr_dict["operator"] == "+"
    assert bin_expr_dict["left"]["type"] == "Variable"
    assert bin_expr_dict["left"]["name"] == "x"

    then_print = if_stmt.then_body[1]
    assert isinstance(then_print, PrintStatement)
    # else body has 1 statement: print "Done"
    assert len(if_stmt.else_body) == 1
    else_print = if_stmt.else_body[0]
    assert isinstance(else_print, PrintStatement)
    assert else_print.expressions[0].to_dict()["value"] == "Done"

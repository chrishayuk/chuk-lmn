# tests/test_statements_parser.py

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser
from lmn.compiler.ast import (
    Program,
    IfStatement,
    LetStatement,
    AssignmentStatement,
    PrintStatement,
    ReturnStatement,
    ForStatement,
    LiteralExpression,
    VariableExpression,
    BinaryExpression,
)

def test_parse_empty():
    code = ""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect a Program node with an empty body
    assert isinstance(program_ast, Program)
    assert len(program_ast.body) == 0


def test_parse_let_statement():
    """
    Basic let statement without a colon-based type annotation:
        let x = 5
    """
    code = "let x = 5"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, LetStatement)

    # Check the variable name
    assert stmt.variable.name == "x"

    # The expression should be a literal with value=5
    assert isinstance(stmt.expression, LiteralExpression)
    assert stmt.expression.value == 5

    # No type annotation => stmt.type_annotation is None
    assert stmt.type_annotation is None

    # The parser doesn't do type inference, so these are typically None
    assert stmt.variable.inferred_type is None
    assert stmt.expression.inferred_type is None


def test_parse_let_statement_with_type_colon():
    """
    Tests a let statement with a colon-based type annotation:
        let counter: int = 0
    """
    code = "let counter: int = 0"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, LetStatement)

    # 'counter'
    assert stmt.variable.name == "counter"

    # type_annotation => "int"
    assert stmt.type_annotation == "int"

    # The expression => LiteralExpression(0)
    assert isinstance(stmt.expression, LiteralExpression)
    assert stmt.expression.value == 0

    # No actual type inference done yet
    assert stmt.variable.inferred_type is None
    assert stmt.expression.inferred_type is None


def test_parse_let_statement_with_type_colon_no_init():
    """
    Tests a let statement with a colon-based type annotation but no initializer:
        let ratio: float
    """
    code = "let ratio: float"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, LetStatement)

    # 'ratio'
    assert stmt.variable.name == "ratio"

    # type_annotation => "float"
    assert stmt.type_annotation == "float"

    # No initializer => expression is None
    assert stmt.expression is None


def test_parse_assignment_statement():
    code = "counter = 10"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    stmt = program_ast.body[0]
    assert isinstance(stmt, AssignmentStatement)
    assert stmt.variable_name == "counter"
    assert isinstance(stmt.expression, LiteralExpression)
    assert stmt.expression.value == 10
    assert stmt.expression.inferred_type is None


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
    assert isinstance(exprs[0], LiteralExpression)
    assert exprs[0].value == 10
    assert exprs[0].inferred_type is None
    assert isinstance(exprs[1], LiteralExpression)
    assert exprs[1].value == 20
    assert exprs[1].inferred_type is None


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
    assert isinstance(stmt.condition, BinaryExpression)
    assert stmt.condition.operator == "<"
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
    assert isinstance(stmt.condition, BinaryExpression)
    assert stmt.condition.operator == ">="
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
    assert isinstance(stmt.expression, BinaryExpression)
    assert stmt.expression.operator == "+"
    # left side: VariableExpression("x"), right side: LiteralExpression(1)


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
    assert isinstance(stmt.start_expr, LiteralExpression)
    assert stmt.start_expr.value == 1
    assert isinstance(stmt.end_expr, LiteralExpression)
    assert stmt.end_expr.value == 5
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
    assert isinstance(stmt.start_expr, VariableExpression)
    assert stmt.start_expr.name == "locations"
    assert stmt.end_expr is None
    # body has 1 statement: print city
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], PrintStatement)


def test_parse_complex():
    """
    Replaces old snippet that used `set`.
    Original:
        set x = 3
        if (x < 5)
          set x = x + 1
          print x
        else
          print "Done"
        end

    New snippet uses `let`:
    """
    code = """
    let x = 3
    if (x < 5)
      let x = x + 1
      print x
    else
      print "Done"
    end
    """

    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 2

    # 1) let x = 3
    let_stmt = program_ast.body[0]
    assert isinstance(let_stmt, LetStatement)
    assert let_stmt.variable.name == "x"
    assert isinstance(let_stmt.expression, LiteralExpression)
    assert let_stmt.expression.value == 3
    assert let_stmt.variable.inferred_type is None
    assert let_stmt.expression.inferred_type is None

    # 2) if statement
    if_stmt = program_ast.body[1]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, BinaryExpression)
    assert if_stmt.condition.operator == "<"
    # then body has 2 statements: let x = x + 1, print x
    assert len(if_stmt.then_body) == 2
    then_let = if_stmt.then_body[0]
    assert isinstance(then_let, LetStatement)
    assert isinstance(then_let.expression, BinaryExpression)
    assert then_let.expression.operator == "+"
    assert isinstance(then_let.expression.left, VariableExpression)
    assert then_let.expression.left.name == "x"
    assert then_let.variable.inferred_type is None
    assert then_let.expression.inferred_type is None

    then_print = if_stmt.then_body[1]
    assert isinstance(then_print, PrintStatement)
    # else body has 1 statement: print "Done"
    assert len(if_stmt.else_body) == 1
    else_print = if_stmt.else_body[0]
    assert isinstance(else_print, PrintStatement)
    assert isinstance(else_print.expressions[0], LiteralExpression)
    assert else_print.expressions[0].value == "Done"
    assert else_print.expressions[0].inferred_type is None

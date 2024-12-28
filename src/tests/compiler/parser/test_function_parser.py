# file: tests/test_function_parser.py

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser
from lmn.compiler.ast import (
    FunctionDefinition,
    IfStatement,
    LetStatement,
    PrintStatement,
    ReturnStatement,
    BinaryExpression,
    FnExpression,
    LiteralExpression,
    VariableExpression,
)


def test_empty_function():
    """
    function empty()
    end
    """
    code = """function empty() end"""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # 1 function definition
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "empty"
    # No parameters
    assert len(func_def.params) == 0
    # Empty body
    assert len(func_def.body) == 0


def test_function_one_param():
    """
    function greet(name)
      print "Hello," name
    end
    """
    code = """
    function greet(name)
      print "Hello," name
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect 1 function definition
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "greet"
    # Expect exactly 1 param object
    assert len(func_def.params) == 1
    param0 = func_def.params[0]
    # e.g. param0 => { "name": "name", "type_annotation": None } 
    assert param0.name == "name"
    # If your model has .type_annotation, we assume None
    assert param0.type_annotation in (None, "any")

    # Body => 1 statement => print "Hello," name
    assert len(func_def.body) == 1
    stmt = func_def.body[0]
    assert isinstance(stmt, PrintStatement)
    # 2 expressions => "Hello," and name
    assert len(stmt.expressions) == 2
    lit, var = stmt.expressions
    assert isinstance(lit, LiteralExpression)
    assert lit.value == "Hello,"
    assert isinstance(var, VariableExpression)
    assert var.name == "name"


def test_function_two_params_and_return():
    """
    function add(a, b)
      return a + b
    end
    """
    code = """
    function add(a, b)
      return a + b
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "add"

    # Expect 2 param objects
    assert len(func_def.params) == 2
    p0, p1 = func_def.params
    assert p0.name == "a"
    assert p1.name == "b"

    # Body => 1 statement => return a + b
    assert len(func_def.body) == 1
    ret_stmt = func_def.body[0]
    assert isinstance(ret_stmt, ReturnStatement)

    # a + b => BinaryExpression("+")
    bin_expr = ret_stmt.expression
    assert isinstance(bin_expr, BinaryExpression)
    assert bin_expr.operator == "+"
    # left => variable "a"
    assert isinstance(bin_expr.left, VariableExpression)
    assert bin_expr.left.name == "a"
    # right => variable "b"
    assert isinstance(bin_expr.right, VariableExpression)
    assert bin_expr.right.name == "b"


def test_function_if_statement():
    """
    function check(x)
      if (x > 10)
        print "Big"
      else
        print "Small"
      end
    end
    """
    code = """
    function check(x)
      if (x > 10)
        print "Big"
      else
        print "Small"
      end
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "check"

    # 1 param => x
    assert len(func_def.params) == 1
    param0 = func_def.params[0]
    assert param0.name == "x"

    # Body => 1 if-statement
    assert len(func_def.body) == 1
    if_stmt = func_def.body[0]
    assert isinstance(if_stmt, IfStatement)

    cond = if_stmt.condition
    assert isinstance(cond, BinaryExpression)
    assert cond.operator == ">"

    # then => print "Big"
    assert len(if_stmt.then_body) == 1
    assert isinstance(if_stmt.then_body[0], PrintStatement)
    # else => print "Small"
    assert len(if_stmt.else_body) == 1
    assert isinstance(if_stmt.else_body[0], PrintStatement)


def test_function_with_recursion():
    """
    function factorial(n)
      if (n <= 1)
        return 1
      else
        return n * factorial(n - 1)
      end
    end
    """
    code = """
    function factorial(n)
      if (n <= 1)
        return 1
      else
        return n * factorial(n - 1)
      end
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "factorial"

    # 1 param => n
    assert len(func_def.params) == 1
    assert func_def.params[0].name == "n"

    # Body => 1 if statement
    assert len(func_def.body) == 1
    if_stmt = func_def.body[0]
    assert isinstance(if_stmt, IfStatement)

    cond = if_stmt.condition
    assert isinstance(cond, BinaryExpression)
    assert cond.operator == "<="

    # then => return 1
    assert len(if_stmt.then_body) == 1
    assert isinstance(if_stmt.then_body[0], ReturnStatement)

    # else => return n * factorial(n - 1)
    else_body = if_stmt.else_body
    assert len(else_body) == 1
    ret_stmt = else_body[0]
    assert isinstance(ret_stmt, ReturnStatement)

    bin_expr = ret_stmt.expression
    assert isinstance(bin_expr, BinaryExpression)
    assert bin_expr.operator == "*"
    # left => n
    assert isinstance(bin_expr.left, VariableExpression)
    assert bin_expr.left.name == "n"
    # right => FnExpression => factorial(n - 1)
    right_fn = bin_expr.right
    assert isinstance(right_fn, FnExpression)
    # The "name" might itself be a VariableExpression or literal.
    # E.g. right_fn.name => VariableExpression("factorial") or "factorial"
    # Adjust if your AST structure is different.


def test_function_multiple_statements_body():
    """
    function doStuff(a)
      let x = a
      print x
      return x * 2
    end
    """
    code = """
    function doStuff(a)
      let x = a
      print x
      return x * 2
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect 1 function definition
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "doStuff"

    # 1 param => a
    assert len(func_def.params) == 1
    param0 = func_def.params[0]
    assert param0.name == "a"

    # body => 3 statements => let x=a, print x, return x*2
    assert len(func_def.body) == 3
    stmt1, stmt2, stmt3 = func_def.body

    # let x = a
    assert isinstance(stmt1, LetStatement)
    assert stmt1.variable.name == "x"
    assert isinstance(stmt1.expression, VariableExpression)
    assert stmt1.expression.name == "a"

    # print x
    assert isinstance(stmt2, PrintStatement)
    assert len(stmt2.expressions) == 1
    expr2 = stmt2.expressions[0]
    assert isinstance(expr2, VariableExpression)
    assert expr2.name == "x"

    # return x*2
    assert isinstance(stmt3, ReturnStatement)
    rexp = stmt3.expression
    assert isinstance(rexp, BinaryExpression)
    assert rexp.operator == "*"
    assert isinstance(rexp.left, VariableExpression)
    assert rexp.left.name == "x"
    # right => 2
    assert isinstance(rexp.right, LiteralExpression)
    assert rexp.right.value == 2

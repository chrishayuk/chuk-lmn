# tests/test_function_parser.py
from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser

# Instead of from old submodules, import from your mega-union approach if re-exported in __init__.py
from lmn.compiler.ast import (
    FunctionDefinition,
    IfStatement,
    SetStatement,
    PrintStatement,
    ReturnStatement,
    BinaryExpression,
    FnExpression,
    LiteralExpression,
    VariableExpression,
)

def test_empty_function():
    """
    Test a function with no parameters and no body statements:
    
    function empty()
    end
    """
    code = """function empty() end"""
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect 1 FunctionDefinition in the program
    # The program stores top-level statements in .body
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "empty"
    # No parameters
    assert func_def.params == []
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

    # Top-level statements => .body
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "greet"
    # 1 parameter: name
    assert func_def.params == ["name"]
    # Body has 1 statement
    assert len(func_def.body) == 1
    stmt = func_def.body[0]
    assert isinstance(stmt, PrintStatement)
    # 2 expressions: "Hello," and name
    assert len(stmt.expressions) == 2
    # First is a literal string, second is a variable
    lit = stmt.expressions[0]
    var = stmt.expressions[1]
    # Check for LiteralExpression
    assert isinstance(lit, LiteralExpression)
    assert lit.value == "Hello,"
    # Check for VariableExpression
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
    assert func_def.params == ["a", "b"]
    assert len(func_def.body) == 1

    stmt = func_def.body[0]
    assert isinstance(stmt, ReturnStatement)
    # Check it's returning a + b
    expr_dict = stmt.expression.to_dict()
    assert expr_dict["type"] == "BinaryExpression"
    assert expr_dict["operator"] == "+"

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

    # 1 function definition
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "check"
    assert func_def.params == ["x"]
    # Body has 1 statement: if-statement
    assert len(func_def.body) == 1
    if_stmt = func_def.body[0]
    assert isinstance(if_stmt, IfStatement)

    # Check condition is x > 10
    cond_dict = if_stmt.condition.to_dict()
    assert cond_dict["type"] == "BinaryExpression"
    assert cond_dict["operator"] == ">"

    # thenBody: 1 statement => print "Big"
    assert len(if_stmt.then_body) == 1
    assert isinstance(if_stmt.then_body[0], PrintStatement)

    # elseBody: 1 statement => print "Small"
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
    # check param "n"
    assert func_def.params == ["n"]
    # body has 1 if-statement
    assert len(func_def.body) == 1
    if_stmt = func_def.body[0]
    assert isinstance(if_stmt, IfStatement)

    # condition: n <= 1
    cond_dict = if_stmt.condition.to_dict()
    assert cond_dict["operator"] == "<="

    # thenBody => return 1
    then_body = if_stmt.then_body
    assert len(then_body) == 1
    assert isinstance(then_body[0], ReturnStatement)

    # elseBody => return n * factorial(n - 1)
    else_body = if_stmt.else_body
    assert len(else_body) == 1
    return_stmt = else_body[0]
    assert isinstance(return_stmt, ReturnStatement)

    # The expression is a BinaryExpression with operator '*'
    bin_expr = return_stmt.expression
    assert isinstance(bin_expr, BinaryExpression)
    assert bin_expr.operator == "*"

    # Left side is a variable 'n'
    assert isinstance(bin_expr.left, VariableExpression)
    assert bin_expr.left.name == "n"

    # Right side is a FnExpression => factorial(n - 1)
    assert isinstance(bin_expr.right, FnExpression)
    # etc. if you want more checks

def test_function_multiple_statements_body():
    """
    function doStuff(a)
      set x = a
      print x
      return x * 2
    end
    """
    code = """
    function doStuff(a)
      set x = a
      print x
      return x * 2
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "doStuff"
    assert func_def.params == ["a"]
    # body has 3 statements: set x a, print x, return x * 2
    assert len(func_def.body) == 3
    stmt1, stmt2, stmt3 = func_def.body

    # stmt1 => set x a
    assert isinstance(stmt1, SetStatement)
    assert stmt1.variable.name == "x"

    # stmt2 => print x
    assert isinstance(stmt2, PrintStatement)
    assert len(stmt2.expressions) == 1
    # Usually we expect 'x' to be a VariableExpression
    assert isinstance(stmt2.expressions[0], VariableExpression)

    # stmt3 => return x * 2
    assert isinstance(stmt3, ReturnStatement)
    rexp = stmt3.expression
    rdict = rexp.to_dict()
    assert rdict["type"] == "BinaryExpression"
    assert rdict["operator"] == "*"

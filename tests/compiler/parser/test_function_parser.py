# tests/test_function_parser.py
from compiler.lexer.tokenizer import Tokenizer
from compiler.parser.parser import Parser
from compiler.ast.statements.function_definition import FunctionDefinition
from compiler.ast.statements.if_statement import IfStatement
from compiler.ast.statements.set_statement import SetStatement
from compiler.ast.statements.print_statement import PrintStatement
from compiler.ast.statements.return_statement import ReturnStatement
from compiler.ast.expressions.binary_expression import BinaryExpression
from compiler.ast.expressions.fn_expression import FnExpression
from compiler.ast.expressions.literal import Literal

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
    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "empty"
    # No parameters
    assert func_def.parameters == []
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

    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "greet"
    # 1 parameter: name
    assert func_def.parameters == ["name"]
    # Body has 1 statement
    assert len(func_def.body) == 1
    stmt = func_def.body[0]
    assert isinstance(stmt, PrintStatement)
    # 2 expressions: "Hello," and name
    assert len(stmt.expressions) == 2
    # First is a literal string, second is a variable
    lit = stmt.expressions[0]
    var = stmt.expressions[1]
    assert isinstance(lit, Literal)
    assert lit.value == "Hello,"
    # var might be a Variable if your parser returns that for identifiers

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

    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "add"
    assert func_def.parameters == ["a", "b"]
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
    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "check"
    assert func_def.parameters == ["x"]
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

    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "factorial"
    # check param "n"
    assert func_def.parameters == ["n"]
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

    # The expression is a binary expression with operator '*'
    bin_expr = return_stmt.expression
    assert isinstance(bin_expr, BinaryExpression)
    op = bin_expr.operator
    # operator is LmnTokenType.MUL (or a token with value='*')
    # we can check bin_expr.to_dict()["operator"] == "*"

    # Left side is Variable(n)
    left_side = bin_expr.left
    # Right side is FnExpression factorial(n-1)
    right_side = bin_expr.right
    assert isinstance(right_side, FnExpression)

def test_function_multiple_statements_body():
    """
    function doStuff(a)
      set x a
      print x
      return x * 2
    end
    """
    code = """
    function doStuff(a)
      set x a
      print x
      return x * 2
    end
    """
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    assert len(program_ast.statements) == 1
    func_def = program_ast.statements[0]
    assert isinstance(func_def, FunctionDefinition)
    assert func_def.name == "doStuff"
    assert func_def.parameters == ["a"]
    # body has 3 statements: set x a, print x, return x * 2
    assert len(func_def.body) == 3
    stmt1, stmt2, stmt3 = func_def.body

    # stmt1 => set x a
    assert isinstance(stmt1, SetStatement)
    assert stmt1.variable.name == "x"

    # stmt2 => print x
    assert isinstance(stmt2, PrintStatement)
    assert len(stmt2.expressions) == 1

    # stmt3 => return x * 2
    assert isinstance(stmt3, ReturnStatement)
    rexp = stmt3.expression
    rdict = rexp.to_dict()
    assert rdict["type"] == "BinaryExpression"
    assert rdict["operator"] == "*"


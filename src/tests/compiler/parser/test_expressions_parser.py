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

def test_parse_string_literal_expr():
    """
    Checks that a simple string literal becomes a LiteralExpression with the correct value.
    """
    code = r'print "Hello, world!"'
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    stmt = program_ast.body[0]
    # We expect a PrintStatement with one expression
    assert stmt.type == "PrintStatement"
    assert len(stmt.expressions) == 1
    expr = stmt.expressions[0]

    # Should be a LiteralExpression
    assert expr.type == "LiteralExpression"
    assert expr.value == "Hello, world!"

def test_parse_emoji_string():
    """
    Verifies that a string containing an emoji is handled as a single LiteralExpression.
    """
    code = r'let greeting = "Hello 🌎!"'
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect a single LetStatement
    stmt = program_ast.body[0]
    assert stmt.type == "LetStatement"
    assert stmt.variable.name == "greeting"

    # The expression should be a LiteralExpression
    expr = stmt.expression
    assert expr.type == "LiteralExpression"
    # Just check the key pieces
    assert "Hello" in expr.value
    assert "🌎" in expr.value
    assert expr.value.endswith("!")

def test_parse_native_array_literal():
    """
    Tests an array literal that contains arbitrary expressions, not just JSON values.
    """
    code = "let arr = [1, 2+3, foo(7), \"hi\"]"
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # We expect let arr = [ ... ]
    stmt = program_ast.body[0]
    assert stmt.type == "LetStatement"
    assert stmt.variable.name == "arr"

    expr = stmt.expression
    assert expr.type == "ArrayLiteralExpression"
    elements = expr.elements
    assert len(elements) == 4

    # element 0 => LiteralExpression(1)
    e0 = elements[0]
    assert e0.type == "LiteralExpression"
    assert e0.value == 1

    # element 1 => BinaryExpression(2 + 3)
    e1 = elements[1]
    assert e1.type == "BinaryExpression"
    assert e1.operator == "+"
    assert e1.left.value == 2
    assert e1.right.value == 3

    # element 2 => FnExpression(foo(7))
    e2 = elements[2]
    assert e2.type == "FnExpression"
    assert e2.name.name == "foo"
    assert len(e2.arguments) == 1
    assert e2.arguments[0].value == 7

    # element 3 => LiteralExpression("hi")
    e3 = elements[3]
    assert e3.type == "LiteralExpression"
    assert e3.value == "hi"

def test_parse_json_array_literal():
    """
    Tests a JSON array literal, which should become a JsonLiteralExpression.
    """
    code = 'let colors = [ "red", "green", "blue" ]'
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    stmt = program_ast.body[0]
    assert stmt.type == "LetStatement"
    assert stmt.variable.name == "colors"

    expr = stmt.expression
    # We expect a JsonLiteralExpression, since it's purely JSON (strings only).
    assert expr.type == "JsonLiteralExpression"
    value = expr.value
    # Should be a list of strings
    assert value == ["red", "green", "blue"]

def test_mixed_features_ast():
    """
    Tests parsing a snippet with:
      1) A string literal with backslash/emoji
      2) JSON object literal
      3) JSON array literal
      4) Native array with expressions
    And checks the resulting AST nodes.
    """
    code = r'''
    function main()
        # 1) A simple string with an emoji and some escapes
        let greeting = "Hello\n🌍 \"Earth\"!"

        # Print it
        print greeting

        # 2) A JSON object literal
        let user = {
            "name": "Alice",
            "age": 42,
            "languages": ["English", "Spanish"],
            "active": true
        }
        print "User data:" user

        # 3) A pure JSON array literal
        let colors = [ "red", "green", "blue" ]
        print "Colors array:" colors

        # 4) A native array with expressions
        let myArray = [ 1, 2+3, foo(7), greeting ]
        print "Native array with expressions:" myArray
    end
    '''

    # 1) Tokenize and parse
    tokens = Tokenizer(code).tokenize()
    parser = Parser(tokens)
    program_ast = parser.parse()

    # 2) We expect program_ast.body to contain one FunctionDefinition node
    assert len(program_ast.body) == 1
    func_def = program_ast.body[0]
    assert func_def.type == "FunctionDefinition"
    assert func_def.name == "main"
    # func_def.body is the list of statements inside main()
    stmts = func_def.body
    # We expect 8 statements in total (roughly):
    #  0 -> let greeting
    #  1 -> print greeting
    #  2 -> let user
    #  3 -> print "User data:" user
    #  4 -> let colors
    #  5 -> print "Colors array:" colors
    #  6 -> let myArray
    #  7 -> print "Native array with expressions:" myArray
    assert len(stmts) == 8

    #
    # Statement 0: let greeting = "Hello\n🌍 \"Earth\"!"
    #
    let_greeting = stmts[0]
    assert let_greeting.type == "LetStatement"
    assert let_greeting.variable.name == "greeting"
    # The expression should be a LiteralExpression
    expr_greeting = let_greeting.expression
    assert expr_greeting.type == "LiteralExpression"
    # The exact stored string might have backslash escapes, or unicode escapes for the emoji.
    # We'll just check that it's a string containing "Hello" and "Earth".
    # For a more robust check, you can do:
    assert "Hello" in expr_greeting.value
    assert "Earth" in expr_greeting.value

    #
    # Statement 1: print greeting
    #
    print_greeting = stmts[1]
    assert print_greeting.type == "PrintStatement"
    # The 'expressions' array: first item => VariableExpression("greeting")
    assert len(print_greeting.expressions) == 1
    var_greeting_expr = print_greeting.expressions[0]
    assert var_greeting_expr.type == "VariableExpression"
    assert var_greeting_expr.name == "greeting"

    #
    # Statement 2: let user = { "name": "Alice", ... }
    #
    let_user = stmts[2]
    assert let_user.type == "LetStatement"
    assert let_user.variable.name == "user"
    user_expr = let_user.expression
    # Should be a JsonLiteralExpression with a dict
    assert user_expr.type == "JsonLiteralExpression"
    assert isinstance(user_expr.value, dict)
    # Check some keys
    assert user_expr.value["name"] == "Alice"
    assert user_expr.value["age"] == 42
    assert user_expr.value["languages"] == ["English", "Spanish"]
    assert user_expr.value["active"] == True

    #
    # Statement 3: print "User data:" user
    #
    print_user = stmts[3]
    assert print_user.type == "PrintStatement"
    assert len(print_user.expressions) == 2
    user_expr_0 = print_user.expressions[0]
    user_expr_1 = print_user.expressions[1]
    assert user_expr_0.type == "LiteralExpression"
    assert "User data:" in user_expr_0.value
    assert user_expr_1.type == "VariableExpression"
    assert user_expr_1.name == "user"

    #
    # Statement 4: let colors = [ "red", "green", "blue" ]
    #
    let_colors = stmts[4]
    assert let_colors.type == "LetStatement"
    assert let_colors.variable.name == "colors"
    colors_expr = let_colors.expression
    # Should be a JsonLiteralExpression with a list
    assert colors_expr.type == "JsonLiteralExpression"
    assert isinstance(colors_expr.value, list)
    assert colors_expr.value == ["red", "green", "blue"]

    #
    # Statement 5: print "Colors array:" colors
    #
    print_colors = stmts[5]
    assert print_colors.type == "PrintStatement"
    assert len(print_colors.expressions) == 2
    color_expr_0 = print_colors.expressions[0]
    color_expr_1 = print_colors.expressions[1]
    assert color_expr_0.type == "LiteralExpression"
    assert "Colors array:" in color_expr_0.value
    assert color_expr_1.type == "VariableExpression"
    assert color_expr_1.name == "colors"

    #
    # Statement 6: let myArray = [ 1, 2+3, foo(7), greeting ]
    #
    let_myArray = stmts[6]
    assert let_myArray.type == "LetStatement"
    assert let_myArray.variable.name == "myArray"
    myArray_expr = let_myArray.expression
    # Should be an ArrayLiteralExpression
    assert myArray_expr.type == "ArrayLiteralExpression"
    elements = myArray_expr.elements
    assert len(elements) == 4

    # element0 => LiteralExpression(1)
    e0 = elements[0]
    assert e0.type == "LiteralExpression"
    assert e0.value == 1

    # element1 => BinaryExpression(2 + 3)
    e1 = elements[1]
    assert e1.type == "BinaryExpression"
    assert e1.operator == "+"
    assert e1.left.value == 2
    assert e1.right.value == 3

    # element2 => FnExpression(foo(7))
    e2 = elements[2]
    assert e2.type == "FnExpression"
    assert e2.name.type == "VariableExpression"
    assert e2.name.name == "foo"
    assert len(e2.arguments) == 1
    assert e2.arguments[0].type == "LiteralExpression"
    assert e2.arguments[0].value == 7

    # element3 => VariableExpression(greeting)
    e3 = elements[3]
    assert e3.type == "VariableExpression"
    assert e3.name == "greeting"

    #
    # Statement 7: print "Native array with expressions:" myArray
    #
    print_myArray = stmts[7]
    assert print_myArray.type == "PrintStatement"
    assert len(print_myArray.expressions) == 2
    arr_expr_0 = print_myArray.expressions[0]
    arr_expr_1 = print_myArray.expressions[1]

    assert arr_expr_0.type == "LiteralExpression"
    assert "Native array with expressions:" in arr_expr_0.value
    assert arr_expr_1.type == "VariableExpression"
    assert arr_expr_1.name == "myArray"

    print("AST for mixed features snippet looks good!")


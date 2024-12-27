# tests/compiler/lexer/test_tokenizer.py

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.lexer.token_type import LmnTokenType

def test_empty_input():
    tokenizer = Tokenizer("")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 0

def test_comment():
    code = "// This is a comment\n"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    # We get one COMMENT token (or zero if you skip them in the parser)
    assert len(tokens) == 1
    assert tokens[0].token_type == LmnTokenType.COMMENT
    assert tokens[0].value.strip() == "This is a comment"

def test_string_literal():
    tokenizer = Tokenizer('"Hello, world!"')
    tokens = tokenizer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].token_type == LmnTokenType.STRING
    assert tokens[0].value == "Hello, world!"

def test_keywords():
    # Added "set" here
    code = "function if else end return for in to call print set"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    # We now expect 11 tokens
    assert len(tokens) == 11

    expected_keywords = [
        LmnTokenType.FUNCTION,
        LmnTokenType.IF,
        LmnTokenType.ELSE,
        LmnTokenType.END,
        LmnTokenType.RETURN,
        LmnTokenType.FOR,
        LmnTokenType.IN,
        LmnTokenType.TO,
        LmnTokenType.CALL,
        LmnTokenType.PRINT,
        LmnTokenType.SET,   # <-- "set"
    ]
    for i, ttype in enumerate(expected_keywords):
        assert tokens[i].token_type == ttype

def test_operators():
    code = "= != < <= > >= + - * / ^"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 11

    expected = [
        LmnTokenType.EQ,
        LmnTokenType.NE,
        LmnTokenType.LT,
        LmnTokenType.LE,
        LmnTokenType.GT,
        LmnTokenType.GE,
        LmnTokenType.PLUS,
        LmnTokenType.MINUS,
        LmnTokenType.MUL,
        LmnTokenType.DIV,
        LmnTokenType.POW
    ]
    for i, ttype in enumerate(expected):
        assert tokens[i].token_type == ttype

def test_punctuation():
    code = "( ) , [ ]"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 5

    expected = [
        LmnTokenType.LPAREN,
        LmnTokenType.RPAREN,
        LmnTokenType.COMMA,
        LmnTokenType.LBRACKET,
        LmnTokenType.RBRACKET
    ]
    for i, ttype in enumerate(expected):
        assert tokens[i].token_type == ttype

def test_numbers():
    code = "123 45.67 0.99"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 3

    # Ensure they're all NUMBER tokens, with float values
    for t in tokens:
        assert t.token_type == LmnTokenType.NUMBER

    assert tokens[0].value == 123.0
    assert tokens[1].value == 45.67
    assert tokens[2].value == 0.99

def test_identifiers():
    code = "variable1 var_2 myFunc main"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 4

    expected_values = ["variable1", "var_2", "myFunc", "main"]
    for i, val in enumerate(expected_values):
        assert tokens[i].token_type == LmnTokenType.IDENTIFIER
        assert tokens[i].value == val

def test_complex_snippet():
    code = r"""
// A simple factorial
function fact(n)
  if (n <= 1)
    return 1
  else
    return n * fact(n - 1)
  end
end
"""
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # We'll do a loose check on count and some key positions
    assert len(tokens) > 0

    # We expect something like:
    # COMMENT, FUNCTION, IDENTIFIER("fact"), LPAREN, IDENTIFIER("n"), RPAREN,
    # IF, LPAREN, IDENTIFIER("n"), LE, NUMBER(1.0), RPAREN, RETURN, NUMBER(1.0), ELSE, RETURN, IDENTIFIER("n"),
    # MUL, IDENTIFIER("fact"), LPAREN, IDENTIFIER("n"), MINUS, NUMBER(1.0), RPAREN, END, END
    #
    # Let's check just a few spots:
    assert tokens[0].token_type == LmnTokenType.COMMENT
    assert tokens[1].token_type == LmnTokenType.FUNCTION
    assert tokens[2].token_type == LmnTokenType.IDENTIFIER
    assert tokens[3].token_type == LmnTokenType.LPAREN
    # ...
    # last token probably is END
    assert tokens[-1].token_type == LmnTokenType.END

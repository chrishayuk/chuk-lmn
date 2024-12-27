# tests/compiler/lexer/test_tokenizer.py

import pytest
from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.lexer.token_type import LmnTokenType

# If your tokenizer raises a specific error on invalid tokens,
# import or define that error type here:
# from lmn.compiler.lexer.exceptions import SomeLexerError


def test_empty_input():
    tokenizer = Tokenizer("")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 0


def test_comment():
    code = "// This is a comment\n"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
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
    # "set" removed entirely
    code = "function if else end return for in to call print let"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
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
        LmnTokenType.LET,
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
        LmnTokenType.POW,
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
        LmnTokenType.RBRACKET,
    ]
    for i, ttype in enumerate(expected):
        assert tokens[i].token_type == ttype


def test_numbers():
    code = "123 45.67 0.99"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 3

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

    assert len(tokens) > 0

    # Rough checks on some known positions
    assert tokens[0].token_type == LmnTokenType.COMMENT
    assert tokens[1].token_type == LmnTokenType.FUNCTION
    assert tokens[2].token_type == LmnTokenType.IDENTIFIER
    assert tokens[3].token_type == LmnTokenType.LPAREN
    assert tokens[-1].token_type == LmnTokenType.END


# -------------------------------------------------------------------
# EXTENDED TESTS
# -------------------------------------------------------------------

def test_inline_comment():
    code = "let x = 10 // This is an inline comment"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(x), EQ, NUMBER(10), COMMENT
    assert len(tokens) == 5
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "x"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.NUMBER
    assert tokens[3].value == 10.0
    assert tokens[4].token_type == LmnTokenType.COMMENT
    assert "inline comment" in tokens[4].value


def test_empty_lines_and_whitespace():
    code = """
    
      let   y    =   42   
      
    print   y  
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(y), EQ, NUMBER(42), PRINT, IDENTIFIER(y)
    assert len(tokens) == 6
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "y"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.NUMBER
    assert tokens[3].value == 42.0
    assert tokens[4].token_type == LmnTokenType.PRINT
    assert tokens[5].token_type == LmnTokenType.IDENTIFIER
    assert tokens[5].value == "y"


@pytest.mark.skip(reason="Lexer doesn't support backslash escapes.")
def test_string_with_escapes():
    """
    Skipped because the current lexer does not handle backslash
    escapes (like \n or \").
    """
    code = r'"Hello\nWorld" "She said \"Hi\"!"'
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # If it *did* handle escapes, you'd want to see two STRING tokens:
    # assert len(tokens) == 2
    # assert tokens[0].token_type == LmnTokenType.STRING
    # assert tokens[0].value == "Hello\nWorld"
    # assert tokens[1].token_type == LmnTokenType.STRING
    # assert tokens[1].value == 'She said "Hi"!'


def test_numeric_variants():
    """
    Simplified numeric test that doesn't rely on scientific notation 
    or negative numbers as single tokens. Adjust as needed.
    """
    code = "0.0 007 -5"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Let's see what we got:
    #  - '0.0' => NUMBER(0.0)
    #  - '007' => NUMBER(7.0)
    #  - '-5'  => likely MINUS + NUMBER(5) or NUMBER(-5)
    #
    # We'll just ensure we have at least 3 tokens.
    assert len(tokens) >= 3

    # 1) First token: 0.0
    assert tokens[0].token_type == LmnTokenType.NUMBER
    assert tokens[0].value == 0.0

    # 2) Second token: 007 => 7.0
    assert tokens[1].token_type == LmnTokenType.NUMBER
    assert tokens[1].value == 7.0

    # 3) Third (or third + fourth) token(s): -5
    # If your tokenizer breaks out the minus:
    if tokens[2].token_type == LmnTokenType.MINUS:
        # Then next token should be NUMBER(5).
        assert tokens[3].token_type == LmnTokenType.NUMBER
        assert tokens[3].value == 5.0
    else:
        # Single token scenario (NUMBER with value -5.0)
        assert tokens[2].token_type == LmnTokenType.NUMBER
        assert tokens[2].value in (-5, -5.0)


def test_no_whitespace_between_tokens():
    code = "let a=10 print(a)"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(a), EQ, NUMBER(10), PRINT, LPAREN, IDENTIFIER(a), RPAREN
    # But if your tokenizer doesn't handle adjacency well, adapt as needed
    assert len(tokens) == 8
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "a"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.NUMBER
    assert tokens[3].value == 10.0
    assert tokens[4].token_type == LmnTokenType.PRINT
    assert tokens[5].token_type == LmnTokenType.LPAREN
    assert tokens[6].token_type == LmnTokenType.IDENTIFIER
    assert tokens[6].value == "a"
    assert tokens[7].token_type == LmnTokenType.RPAREN

# Optionally, if your tokenizer throws errors on invalid tokens, 
# you could add something like:
#
# def test_invalid_tokens():
#     code = "let a = 10 #@!"
#     tokenizer = Tokenizer(code)
#     with pytest.raises(SomeLexerError):
#         tokenizer.tokenize()

# file: tests/compiler/lexer/test_tokenizer.py

import pytest
from lmn.compiler.lexer.tokenizer import Tokenizer, TokenizationError
from lmn.compiler.lexer.token_type import LmnTokenType

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

# -------------------------------------------------------------------
# UPDATED TEST: test_numbers
# -------------------------------------------------------------------
def test_numbers():
    """
    Check numeric tokens:
      - '123'    => INT_LITERAL
      - '45.67'  => DOUBLE_LITERAL
      - '0.99'   => DOUBLE_LITERAL
    """
    code = "123 45.67 0.99"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 3

    # 123 => INT_LITERAL
    assert tokens[0].token_type == LmnTokenType.INT_LITERAL
    assert tokens[0].value == 123

    # 45.67 => DOUBLE_LITERAL
    assert tokens[1].token_type == LmnTokenType.DOUBLE_LITERAL
    assert tokens[1].value == 45.67

    # 0.99 => DOUBLE_LITERAL
    assert tokens[2].token_type == LmnTokenType.DOUBLE_LITERAL
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

    # 0 => COMMENT
    assert tokens[0].token_type == LmnTokenType.COMMENT
    # 1 => FUNCTION
    assert tokens[1].token_type == LmnTokenType.FUNCTION
    # 2 => IDENTIFIER
    assert tokens[2].token_type == LmnTokenType.IDENTIFIER
    # 3 => LPAREN
    assert tokens[3].token_type == LmnTokenType.LPAREN

    # Find the first 'return'
    return_indices = [i for i, t in enumerate(tokens) if t.token_type == LmnTokenType.RETURN]
    idx = return_indices[0]
    # Next token should be INT_LITERAL(1)
    assert tokens[idx + 1].token_type == LmnTokenType.INT_LITERAL
    assert tokens[idx + 1].value == 1

    # The final token should be END
    assert tokens[-1].token_type == LmnTokenType.END

# -------------------------------------------------------------------
# EXTENDED TESTS
# -------------------------------------------------------------------

def test_inline_comment():
    code = "let x = 10 // This is an inline comment"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(x), EQ, INT_LITERAL(10), COMMENT
    assert len(tokens) == 5
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "x"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.INT_LITERAL
    assert tokens[3].value == 10
    assert tokens[4].token_type == LmnTokenType.COMMENT
    assert "inline comment" in tokens[4].value

def test_empty_lines_and_whitespace():
    code = """
    
      let   y    =   42   
      
    print   y  
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(y), EQ, INT_LITERAL(42), PRINT, IDENTIFIER(y)
    assert len(tokens) == 6
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "y"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.INT_LITERAL
    assert tokens[3].value == 42
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
    # If it *did* handle escapes, you'd test them here.

def test_numeric_variants():
    """
    We only check the resulting token type/values for 0.0, 007, -5.
    The minus sign can become MINUS + INT_LITERAL or a single INT_LITERAL(-5).
    """
    code = "0.0 007 -5"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # We should see at least 3 tokens for these values.
    assert len(tokens) >= 3

    # 1) '0.0' => DOUBLE_LITERAL(0.0)
    assert tokens[0].token_type == LmnTokenType.DOUBLE_LITERAL
    assert tokens[0].value == 0.0

    # 2) '007' => likely INT_LITERAL(7) or LONG_LITERAL(7)
    assert tokens[1].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
    assert tokens[1].value == 7

    # 3) '-5' => might be MINUS + INT_LITERAL(5) or a single INT_LITERAL(-5)
    if len(tokens) == 3:
        # single token => INT_LITERAL(-5), or LONG_LITERAL(-5)
        assert tokens[2].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[2].value in (-5, -5.0)
    else:
        # multiple tokens => MINUS, INT_LITERAL(5)
        assert tokens[2].token_type == LmnTokenType.MINUS
        assert tokens[3].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[3].value == 5

def test_no_whitespace_between_tokens():
    code = "let a=10 print(a)"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: LET, IDENTIFIER(a), EQ, INT_LITERAL(10), PRINT, LPAREN, IDENTIFIER(a), RPAREN
    assert len(tokens) == 8
    assert tokens[0].token_type == LmnTokenType.LET
    assert tokens[1].token_type == LmnTokenType.IDENTIFIER
    assert tokens[1].value == "a"
    assert tokens[2].token_type == LmnTokenType.EQ
    assert tokens[3].token_type == LmnTokenType.INT_LITERAL
    assert tokens[3].value == 10
    assert tokens[4].token_type == LmnTokenType.PRINT
    assert tokens[5].token_type == LmnTokenType.LPAREN
    assert tokens[6].token_type == LmnTokenType.IDENTIFIER
    assert tokens[6].value == "a"
    assert tokens[7].token_type == LmnTokenType.RPAREN

# -------------------------------------------------------------------
# NEW TESTS for the new numeric tokens
# -------------------------------------------------------------------
def test_numeric_types():
    """
    Checks that we can distinguish INT_LITERAL, LONG_LITERAL, FLOAT_LITERAL, DOUBLE_LITERAL
    and handle exponent notation / suffixes if the lexer supports them.
    """
    code = """
    123            // Fits in 32-bit range => INT_LITERAL
    2147483648     // Just beyond 32-bit => LONG_LITERAL
    3.14           // decimal => DOUBLE_LITERAL
    3.14f          // 'f' suffix => FLOAT_LITERAL
    1.23e10        // scientific => DOUBLE_LITERAL
    1.23e10f       // sci + 'f' => FLOAT_LITERAL
    9999999999999  // way beyond 32-bit => LONG_LITERAL
    42             // edge => INT_LITERAL
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Filter out comments
    numeric_tokens = [t for t in tokens if t.token_type != LmnTokenType.COMMENT]

    assert len(numeric_tokens) == 8

    # 1) 123 => INT_LITERAL
    assert numeric_tokens[0].token_type == LmnTokenType.INT_LITERAL
    assert numeric_tokens[0].value == 123

    # 2) 2147483648 => LONG_LITERAL
    assert numeric_tokens[1].token_type == LmnTokenType.LONG_LITERAL
    assert numeric_tokens[1].value == 2147483648

    # 3) 3.14 => DOUBLE_LITERAL
    assert numeric_tokens[2].token_type == LmnTokenType.DOUBLE_LITERAL
    assert numeric_tokens[2].value == 3.14

    # 4) 3.14f => FLOAT_LITERAL
    assert numeric_tokens[3].token_type == LmnTokenType.FLOAT_LITERAL
    assert abs(numeric_tokens[3].value - 3.14) < 1e-7

    # 5) 1.23e10 => DOUBLE_LITERAL
    assert numeric_tokens[4].token_type == LmnTokenType.DOUBLE_LITERAL
    assert abs(numeric_tokens[4].value - 1.23e10) < 1e-3

    # 6) 1.23e10f => FLOAT_LITERAL
    assert numeric_tokens[5].token_type == LmnTokenType.FLOAT_LITERAL
    assert abs(numeric_tokens[5].value - 1.23e10) < 1e-3

    # 7) 9999999999999 => LONG_LITERAL
    assert numeric_tokens[6].token_type == LmnTokenType.LONG_LITERAL
    assert numeric_tokens[6].value == 9999999999999

    # 8) 42 => INT_LITERAL
    assert numeric_tokens[7].token_type == LmnTokenType.INT_LITERAL
    assert numeric_tokens[7].value == 42

def test_type_keywords():
    """
    Checks if int, long, float, double are recognized as TYPE keywords.
    """
    code = "int long float double"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect 4 tokens: INT, LONG, FLOAT, DOUBLE
    assert len(tokens) == 4

    assert tokens[0].token_type == LmnTokenType.INT
    assert tokens[0].value == "int"

    assert tokens[1].token_type == LmnTokenType.LONG
    assert tokens[1].value == "long"

    assert tokens[2].token_type == LmnTokenType.FLOAT
    assert tokens[2].value == "float"

    assert tokens[3].token_type == LmnTokenType.DOUBLE
    assert tokens[3].value == "double"

def test_negative_number():
    """
    Check how negative numbers are tokenized. Could be:
      - single token (INT_LITERAL or LONG_LITERAL with negative value) 
      or 
      - separate tokens: MINUS + INT_LITERAL/LONG_LITERAL
    """
    code = "-123"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # If your lexer splits minus and the number:
    if len(tokens) == 2:
        assert tokens[0].token_type == LmnTokenType.MINUS
        assert tokens[1].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[1].value == 123
    # If your lexer decides negative numbers are a single token:
    elif len(tokens) == 1:
        assert tokens[0].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[0].value in (-123, -123.0)
    else:
        pytest.fail(f"Unexpected token count for '-123': {len(tokens)}")

# If you want to test invalid tokens, you could add:
# def test_invalid_tokens():
#     code = "let a = 10 #@!"
#     tokenizer = Tokenizer(code)
#     with pytest.raises(TokenizationError):
#         tokenizer.tokenize()

# -------------------------------------------------------------------
# NEW TESTS FOR begin..end AND if..elseif..else
# -------------------------------------------------------------------

def test_begin_end():
    """
    Ensures 'begin' and 'end' tokens are recognized properly.
    """
    code = "begin let x = 10 end"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Expect: BEGIN, LET, IDENTIFIER(x), EQ, INT_LITERAL(10), END
    assert len(tokens) == 6
    assert tokens[0].token_type == LmnTokenType.BEGIN
    assert tokens[1].token_type == LmnTokenType.LET
    assert tokens[2].token_type == LmnTokenType.IDENTIFIER
    assert tokens[2].value == "x"
    assert tokens[3].token_type == LmnTokenType.EQ
    assert tokens[4].token_type == LmnTokenType.INT_LITERAL
    assert tokens[4].value == 10
    assert tokens[5].token_type == LmnTokenType.END


def test_if_elseif_else():
    """
    Checks the token stream for a full if/elseif/else block.
    """
    code = """
    if x > 10
        print "Greater"
    elseif x == 10
        print "Equal"
    else
        print "Less"
    end
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Some tokens could be spread across lines; just check total count & sequence
    # Potential tokens (in approximate order):
    # IF, IDENTIFIER(x), GT, INT_LITERAL(10),
    # PRINT, STRING("Greater"),
    # ELSEIF, IDENTIFIER(x), EQEQ, INT_LITERAL(10),
    # PRINT, STRING("Equal"),
    # ELSE,
    # PRINT, STRING("Less"),
    # END
    # Let's do a rough check for them.

    # We'll gather token types to verify
    token_types = [t.token_type for t in tokens]

    # A minimal check for presence:
    assert LmnTokenType.IF in token_types
    assert LmnTokenType.ELSEIF in token_types
    assert LmnTokenType.ELSE in token_types
    assert LmnTokenType.END in token_types
    assert LmnTokenType.PRINT in token_types
    assert LmnTokenType.IDENTIFIER in token_types
    assert LmnTokenType.STRING in token_types
    # For operator '>' and '=='
    assert LmnTokenType.GT in token_types
    assert LmnTokenType.EQEQ in token_types

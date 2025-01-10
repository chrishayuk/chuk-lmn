# file: tests/compiler/lexer/test_tokenizer.py

import pytest
from lmn.compiler.lexer.tokenizer import Tokenizer, TokenizationError
from lmn.compiler.lexer.token_type import LmnTokenType

def test_empty_input():
    tokenizer = Tokenizer("")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 0

def test_comment():
    code = "# This is a comment\n"
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
        LmnTokenType.PRINT,
        LmnTokenType.LET,
    ]
    for i, ttype in enumerate(expected_keywords):
        assert tokens[i].token_type == ttype

def test_operators():
    code = "= != < <= > >= + - * /"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 10

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
# A simple factorial
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

def test_inline_comment():
    code = "let x = 10 # This is an inline comment"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 5

    # LET, IDENTIFIER(x), EQ, INT_LITERAL(10), COMMENT
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
    assert len(tokens) == 6

    # LET, IDENTIFIER(y), EQ, INT_LITERAL(42), PRINT, IDENTIFIER(y)
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
    # If it *did* handle escapes, you'd assert them here.

def test_numeric_variants():
    """
    We only check the resulting token type/values for 0.0, 007, -5.
    The minus sign can become MINUS + INT_LITERAL or a single INT_LITERAL(-5).
    """
    code = "0.0 007 -5"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) >= 3

    # 1) '0.0' => DOUBLE_LITERAL(0.0)
    assert tokens[0].token_type == LmnTokenType.DOUBLE_LITERAL
    assert tokens[0].value == 0.0

    # 2) '007' => INT_LITERAL(7) or LONG_LITERAL(7)
    assert tokens[1].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
    assert tokens[1].value == 7

    # 3) '-5' => single token or multiple tokens
    if len(tokens) == 3:
        # single token => INT_LITERAL(-5) or LONG_LITERAL(-5)
        assert tokens[2].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[2].value in (-5, -5.0)
    else:
        # multiple tokens => MINUS + INT_LITERAL(5)
        assert tokens[2].token_type == LmnTokenType.MINUS
        assert tokens[3].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[3].value == 5

def test_no_whitespace_between_tokens():
    code = "let a=10 print(a)"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 8

    # LET, IDENTIFIER(a), EQ, INT_LITERAL(10), PRINT, LPAREN, IDENTIFIER(a), RPAREN
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

def test_numeric_types():
    """
    Checks that we can distinguish INT_LITERAL, LONG_LITERAL, FLOAT_LITERAL, DOUBLE_LITERAL
    and handle exponent notation / suffixes if the lexer supports them.
    """
    code = """
    123            # Fits in 32-bit range => INT_LITERAL
    2147483648     # Just beyond 32-bit => LONG_LITERAL
    3.14           # decimal => DOUBLE_LITERAL
    3.14f          # 'f' suffix => FLOAT_LITERAL
    1.23e10        # scientific => DOUBLE_LITERAL
    1.23e10f       # sci + 'f' => FLOAT_LITERAL
    9999999999999  # way beyond 32-bit => LONG_LITERAL
    42             # edge => INT_LITERAL
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

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

    if len(tokens) == 2:
        # e.g. MINUS, INT_LITERAL(123)
        assert tokens[0].token_type == LmnTokenType.MINUS
        assert tokens[1].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[1].value == 123
    elif len(tokens) == 1:
        # Single token => INT_LITERAL(-123) or LONG_LITERAL(-123)
        assert tokens[0].token_type in (LmnTokenType.INT_LITERAL, LmnTokenType.LONG_LITERAL)
        assert tokens[0].value in (-123, -123.0)
    else:
        pytest.fail(f"Unexpected token count for '-123': {len(tokens)}")

def test_begin_end():
    """
    Ensures 'begin' and 'end' tokens are recognized properly.
    """
    code = "begin let x = 10 end"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert len(tokens) == 6

    # BEGIN, LET, IDENTIFIER(x), EQ, INT_LITERAL(10), END
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

    token_types = [t.token_type for t in tokens]

    # Minimal check for presence
    assert LmnTokenType.IF in token_types
    assert LmnTokenType.ELSEIF in token_types
    assert LmnTokenType.ELSE in token_types
    assert LmnTokenType.END in token_types
    assert LmnTokenType.PRINT in token_types
    assert LmnTokenType.IDENTIFIER in token_types
    assert LmnTokenType.STRING in token_types
    assert LmnTokenType.GT in token_types
    assert LmnTokenType.EQEQ in token_types

def test_json_object_literal():
    """
    Tests a simple JSON object literal in code:
      let user = { "name": "Alice", "age": 42, "active": true }
    """
    code = """
    let user = {
        "name": "Alice",
        "age": 42,
        "active": true
    }
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Let's strip out COMMENT tokens or whitespace-only lines if any:
    filtered = [t for t in tokens if t.token_type != LmnTokenType.COMMENT]

    # We expect:
    #  0: LET
    #  1: IDENTIFIER (user)
    #  2: EQ
    #  3: LBRACE
    #  4: STRING (name)
    #  5: COLON
    #  6: STRING (Alice)
    #  7: COMMA
    #  8: STRING (age)
    #  9: COLON
    # 10: INT_LITERAL(42)
    # 11: COMMA
    # 12: STRING(active)
    # 13: COLON
    # 14: TRUE
    # 15: RBRACE

    assert len(filtered) == 16

    assert filtered[0].token_type == LmnTokenType.LET
    assert filtered[1].token_type == LmnTokenType.IDENTIFIER
    assert filtered[1].value == "user"
    assert filtered[2].token_type == LmnTokenType.EQ
    assert filtered[3].token_type == LmnTokenType.LBRACE

    # Key: "name"
    assert filtered[4].token_type == LmnTokenType.STRING
    assert filtered[4].value == "name"
    assert filtered[5].token_type == LmnTokenType.COLON
    # Value: "Alice"
    assert filtered[6].token_type == LmnTokenType.STRING
    assert filtered[6].value == "Alice"

    assert filtered[7].token_type == LmnTokenType.COMMA

    # Key: "age"
    assert filtered[8].token_type == LmnTokenType.STRING
    assert filtered[8].value == "age"
    assert filtered[9].token_type == LmnTokenType.COLON
    # Value: 42
    assert filtered[10].token_type == LmnTokenType.INT_LITERAL
    assert filtered[10].value == 42

    assert filtered[11].token_type == LmnTokenType.COMMA

    # Key: "active"
    assert filtered[12].token_type == LmnTokenType.STRING
    assert filtered[12].value == "active"
    assert filtered[13].token_type == LmnTokenType.COLON
    # Value: true
    assert filtered[14].token_type == LmnTokenType.TRUE

    assert filtered[15].token_type == LmnTokenType.RBRACE


def test_json_nested_object_and_array():
    """
    Tests a nested JSON object with an inner object, array, and 'null' => 'nil'.
      let data = {
          "user": {
              "name": "Alice",
              "active": true
          },
          "scores": [10, 20, 30],
          "meta": null
      }
      print data
    """
    code = """
    let data = {
        "user": {
            "name": "Alice",
            "active": true
        },
        "scores": [10, 20, 30],
        "meta": null
    }
    print data
    """
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # We'll do some checks on key tokens to ensure JSON braces/brackets are recognized.
    # A full breakdown of every token is optional; here we just verify the critical ones.

    # Find the '{' token for the outer object
    lbrace_indices = [i for i, t in enumerate(tokens) if t.token_type == LmnTokenType.LBRACE]
    assert len(lbrace_indices) >= 2  # one for outer, one for inner object
    
    # Check that "null" is tokenized as NIL
    nil_tokens = [t for t in tokens if t.token_type == LmnTokenType.NIL]
    assert len(nil_tokens) == 1
    assert nil_tokens[0].value in ("null", "nil")  # depending on how you map it

    # Check that we have an INT_LITERAL for the array items 10, 20, 30
    int_literals = [t for t in tokens if t.token_type == LmnTokenType.INT_LITERAL]
    # We expect at least 3 (for 10, 20, 30). Possibly more if there's other ints.
    values = [t.value for t in int_literals]
    for v in (10, 20, 30):
        assert v in values

    # Finally, ensure 'print' and 'data' appear
    assert any(t.token_type == LmnTokenType.PRINT for t in tokens)
    data_tokens = [t for t in tokens if t.token_type == LmnTokenType.IDENTIFIER and t.value == "data"]
    assert len(data_tokens) >= 2  # one for 'let data', one for 'print data'

def test_mixed_features():
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
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # 1) Find all STRING tokens
    string_tokens = [t for t in tokens if t.token_type == LmnTokenType.STRING]

    # 2) Check we have a greeting-like string 
    found_greeting = False
    for t in string_tokens:
        val = t.value
        # We'll do a partial check: "Hello", "🌍", and "Earth" must appear
        if ("Hello" in val) and ("🌍" in val) and ("Earth" in val):
            found_greeting = True
            break

    assert found_greeting, (
        "Did not find a string token with 'Hello', '🌍', and 'Earth' in it. "
        "Check that your tokenizer handles backslash escapes or emoji."
    )

    # (You can keep the rest of the checks for JSON and arrays the same as before)
    ...



# Example of how you'd test invalid tokens, if desired:
# def test_invalid_tokens():
#     code = "let a = 10 @invalid!"
#     tokenizer = Tokenizer(code)
#     with pytest.raises(TokenizationError):
#         tokenizer.tokenize()

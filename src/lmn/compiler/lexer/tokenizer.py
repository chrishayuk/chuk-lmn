# lmn/compiler/lexer/tokenizer.py
import re
from lmn.compiler.lexer.token import Token
from lmn.compiler.lexer.token_type import LmnTokenType

class TokenizationError(Exception):
    pass

class Tokenizer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.current_pos = 0

    def tokenize(self):
        tokens = []
        while self.current_pos < len(self.input_string):
            token = self.get_next_token()
            if token:
                tokens.append(token)
            else:
                self.skip_whitespace()
                if self.current_pos < len(self.input_string):
                    raise TokenizationError(
                        f"Unexpected character: {self.input_string[self.current_pos]}"
                    )
        return tokens

    def get_next_token(self):
        self.skip_whitespace()
        if self.current_pos >= len(self.input_string):
            return None

        # 1. Check for # comments
        if self.input_string[self.current_pos:].startswith("#"):
            return self.tokenize_comment()

        # 2. Match string literals: "..."
        string_token = self.tokenize_string()
        if string_token:
            return string_token

        # 3. Check if the substring matches any LMN keywords
        keyword_token = self.match_keywords()
        if keyword_token:
            return keyword_token

        # 4. Check for operators
        operator_token = self.match_operators()
        if operator_token:
            return operator_token

        # 5. Check for punctuation
        punctuation_token = self.match_punctuation()
        if punctuation_token:
            return punctuation_token

        # 6. Match number (updated)
        number_token = self.tokenize_number()
        if number_token:
            return number_token

        # 7. Match identifier
        identifier_token = self.tokenize_identifier()
        if identifier_token:
            return identifier_token

        return None

    def tokenize_comment(self):
        # Move past the "#"
        self.current_pos += 1
        comment_start = self.current_pos

        # Consume until newline or EOF
        while (self.current_pos < len(self.input_string) and
               self.input_string[self.current_pos] not in ("\n", "\r")):
            self.current_pos += 1
        comment_text = self.input_string[comment_start:self.current_pos]
        return Token(LmnTokenType.COMMENT, comment_text)

    def tokenize_string(self):
        """
        Match a string literal wrapped in double quotes ("...").
        Simple version that doesn't handle escapes.
        """
        if self.input_string[self.current_pos] == '"':
            match = re.match(r'"([^"]*)"', self.input_string[self.current_pos:])
            if match:
                full_text = match.group(0)  # e.g. "Hello world"
                content = match.group(1)    # e.g. Hello world (no quotes)
                self.current_pos += len(full_text)
                return Token(LmnTokenType.STRING, content)
        return None

    def match_keywords(self):
        """
        Check if the current substring matches any known keyword.
        Must ensure we don't match partial identifiers.
        """
        for keyword, token_type in LmnTokenType.get_keywords().items():
            substring = self.input_string[self.current_pos:].lower()
            if substring.startswith(keyword):
                end_pos = self.current_pos + len(keyword)
                # ensure we don't match partial identifiers, e.g. "in" in "index"
                if end_pos == len(self.input_string) or not self.input_string[end_pos].isalnum():
                    self.current_pos += len(keyword)
                    return Token(token_type, keyword)
        return None

    def match_operators(self):
        """
        Match multi-character operators first, then single-character.
        """
        operators = sorted(
            LmnTokenType.get_operator_map().items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        for op, token_type in operators:
            if self.input_string[self.current_pos:].startswith(op):
                self.current_pos += len(op)
                return Token(token_type, op)
        return None


    def match_punctuation(self):
        for punc, token_type in LmnTokenType.get_punctuation_map().items():
            if self.input_string[self.current_pos:].startswith(punc):
                self.current_pos += len(punc)
                return Token(token_type, punc)
        return None

    def tokenize_number(self):
        """
        Match numeric literals:
         - int (32-bit range)
         - long (beyond 32-bit)
         - float (with 'f' suffix, decimal/exponent)
         - double (no 'f' suffix, decimal/exponent)
        """
        pattern = re.compile(
            r"""
            ^
            (\d+(\.\d+)?([eE][+-]?\d+)?)  # Base numeric portion: digits(.digits)?(exponent)?
            ([fF])?                      # Optional 'f' or 'F' suffix for single precision
            """,
            re.VERBOSE
        )

        substring = self.input_string[self.current_pos:]
        match = pattern.match(substring)
        if not match:
            return None

        full_match = match.group(0)
        numeric_part = match.group(1)  # e.g., "123", "1.23", "1.2e10"
        f_suffix = match.group(4)      # 'f' or 'F' if present

        # Advance past the matched numeric string
        self.current_pos += len(full_match)

        # Check decimal or exponent => float/double
        if '.' in numeric_part or 'e' in numeric_part.lower():
            if f_suffix:
                # Float literal
                return Token(LmnTokenType.FLOAT_LITERAL, float(numeric_part))
            else:
                # Double literal
                return Token(LmnTokenType.DOUBLE_LITERAL, float(numeric_part))
        else:
            # Integer form
            val = int(numeric_part)
            # 32-bit range check
            if -2**31 <= val <= 2**31 - 1:
                return Token(LmnTokenType.INT_LITERAL, val)
            else:
                return Token(LmnTokenType.LONG_LITERAL, val)

    def tokenize_identifier(self):
        """
        Match standard identifiers: letters, underscores, digits (but not starting with digit).
        """
        match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', self.input_string[self.current_pos:])
        if match:
            identifier = match.group(0)
            self.current_pos += len(identifier)
            return Token(LmnTokenType.IDENTIFIER, identifier)
        return None

    def skip_whitespace(self):
        """
        Advance current_pos while whitespace chars are found.
        """
        while self.current_pos < len(self.input_string):
            if self.input_string[self.current_pos].isspace():
                self.current_pos += 1
            else:
                break

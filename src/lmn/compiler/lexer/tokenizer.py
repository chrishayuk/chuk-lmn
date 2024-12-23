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
            # Attempt to get a token
            token = self.get_next_token()

            if token:
                tokens.append(token)
            else:
                # If no token found, skip whitespace or raise error if unexpected chars
                self.skip_whitespace()
                if self.current_pos < len(self.input_string):
                    raise TokenizationError(
                        f"Unexpected character: {self.input_string[self.current_pos]}"
                    )

        return tokens

    def get_next_token(self):
        self.skip_whitespace()

        # If we've reached the end of the input string
        if self.current_pos >= len(self.input_string):
            return None

        # 1. Check for // comments
        if self.input_string[self.current_pos:].startswith("//"):
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

        # 6. Match number
        number_token = self.tokenize_number()
        if number_token:
            return number_token

        # 7. Match identifier
        identifier_token = self.tokenize_identifier()
        if identifier_token:
            return identifier_token

        return None

    def tokenize_comment(self):
        # We have //, grab everything until the next newline or end of file
        start_pos = self.current_pos
        
        # Move past //
        self.current_pos += 2

        comment_start = self.current_pos

        # Consume until newline or EOF
        while (
            self.current_pos < len(self.input_string)
            and self.input_string[self.current_pos] not in ("\n", "\r")
        ):
            self.current_pos += 1

        # The comment text is everything from comment_start up to (but not including) newline
        comment_text = self.input_string[comment_start : self.current_pos]

        return Token(LmnTokenType.COMMENT, comment_text)

    def tokenize_string(self):
        # Matches a double-quoted string
        if self.input_string[self.current_pos] == '"':
            # Attempt a regex from the current position
            match = re.match(r'"([^"]*)"', self.input_string[self.current_pos:])
            if match:
                full_text = match.group(0)  # e.g. "Hello world"
                content = match.group(1)    # e.g. Hello world (inside quotes)
                self.current_pos += len(full_text)
                return Token(LmnTokenType.STRING, content)
        return None

    def match_keywords(self):
        """
        If the upcoming substring is one of the recognized LMN keywords,
        consume it and return a Token. Otherwise, return None.
        """
        for keyword, token_type in LmnTokenType.get_keywords().items():
            # Case-sensitive or case-insensitive? LMN is typically lowercase, so we can do:
            if self.input_string[self.current_pos :].lower().startswith(keyword):
                # Check that the next char is non-alphanumeric or we're at end
                end_pos = self.current_pos + len(keyword)
                if end_pos == len(self.input_string) or not self.input_string[end_pos].isalnum():
                    self.current_pos += len(keyword)
                    return Token(token_type, keyword)
        return None

    def match_operators(self):
        # Sort operators by length descending, so '!=' or '<=' gets matched before '=' or '<'
        operators = sorted(LmnTokenType.get_operator_map().items(), key=lambda x: len(x[0]), reverse=True)

        # loop through the operators
        for op, token_type in operators:
            # check if we have a match
            if self.input_string[self.current_pos :].startswith(op):
                # check that the next char is non-alphanumeric or we're at end
                self.current_pos += len(op)

                # return the token
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
        Matches digits (e.g. 123 or 3.14).
        """
        match = re.match(r'\d+(\.\d+)?', self.input_string[self.current_pos:])
        if match:
            number_str = match.group(0)
            self.current_pos += len(number_str)
            try:
                value = float(number_str)
                return Token(LmnTokenType.NUMBER, value)
            except ValueError:
                raise TokenizationError(f"Invalid number: {number_str}")
        return None

    def tokenize_identifier(self):
        """
        Matches an identifier: e.g. myVar, city, sum, etc.
        (Allows letters, digits, underscores. Adjust the regex if needed.)
        """
        # Simple pattern: starts with alpha or underscore, then alphanumeric or underscore
        match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', self.input_string[self.current_pos:])
        if match:
            identifier = match.group(0)
            self.current_pos += len(identifier)
            return Token(LmnTokenType.IDENTIFIER, identifier)
        return None

    def skip_whitespace(self):
        while self.current_pos < len(self.input_string):
            c = self.input_string[self.current_pos]
            if c.isspace():
                self.current_pos += 1
            else:
                break

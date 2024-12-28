# lmn/compiler/lexer/token.py
class Token:
    def __init__(self, token_type, value):
        # set the token type
        self.token_type = token_type

        # set the value
        self.value = value

    def __repr__(self):
        # string representation of the token
        return f"Token({self.token_type}, {self.value})"
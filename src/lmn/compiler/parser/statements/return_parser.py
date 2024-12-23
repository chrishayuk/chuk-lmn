# lmn/compiler/parser/statements/return_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import ReturnStatement


class ReturnParser:
    def __init__(self, parent_parser):
        # Store the parent parser
        self.parser = parent_parser

    def parse(self):
        # current_token == RETURN, consume it
        self.parser.advance()

        # Parse the expression to return
        expr = self.parser.expression_parser.parse_expression()

        # Construct a ReturnStatement with the 'expression' field
        return ReturnStatement(expression=expr)

# lmn/compiler/parser/statements/set_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import SetStatement, VariableExpression
from lmn.compiler.parser.parser_utils import expect_token

class SetParser:
    def __init__(self, parent_parser):
        # set the parent parser
        self.parser = parent_parser

    def parse(self):
        # current_token == SET, consume it
        self.parser.advance()

        # expect an identifier for the variable
        var_token = expect_token(
            self.parser, 
            LmnTokenType.IDENTIFIER, 
            "Expected variable name after 'set'"
        )
        # Replace old `Variable(...)` with `VariableExpression(name=...)`
        variable = VariableExpression(name=var_token.value)
        self.parser.advance()

        # parse the expression that will be assigned
        expr = self.parser.expression_parser.parse_expression()

        # Construct the updated SetStatement with named fields
        return SetStatement(
            variable=variable,
            expression=expr
        )

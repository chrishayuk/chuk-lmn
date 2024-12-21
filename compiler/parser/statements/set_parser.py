# compiler/parser/statements/set_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.set_statement import SetStatement
from compiler.ast.variable import Variable
from compiler.parser.parser_utils import expect_token

class SetParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # current_token == SET, consume
        self.parser.advance()

        # expect identifier
        var_token = expect_token(self.parser, LmnTokenType.IDENTIFIER, "Expected variable name after 'set'")
        variable = Variable(var_token.value)
        self.parser.advance()

        expr = self.parser.expression_parser.parse_expression()

        return SetStatement(variable, expr)

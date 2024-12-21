# compiler/parser/statements/if_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.if_statement import IfStatement
from compiler.parser.parser_utils import expect_token, parse_block

class IfParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # Current token is IF, so advance
        self.parser.advance()  # skip 'if'

        # expect '('
        expect_token(self.parser, LmnTokenType.LPAREN, "Expected '(' after 'if'")
        self.parser.advance()

        # parse condition expression
        condition = self.parser.expression_parser.parse_expression()

        # expect ')'
        expect_token(self.parser, LmnTokenType.RPAREN, "Expected ')' after if condition")
        self.parser.advance()

        # parse then-body
        then_body = parse_block(self.parser, until_tokens=[LmnTokenType.ELSE, LmnTokenType.END])

        # parse else-body?
        else_body = []
        if self.parser.current_token and self.parser.current_token.token_type == LmnTokenType.ELSE:
            self.parser.advance()  # consume else
            else_body = parse_block(self.parser, until_tokens=[LmnTokenType.END])

        # expect 'end'
        expect_token(self.parser, LmnTokenType.END, "Expected 'end' after if statement")
        self.parser.advance()

        return IfStatement(condition, then_body, else_body)

# compiler/parser/statements/if_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.if_statement import IfStatement
from compiler.parser.parser_utils import expect_token, parse_block

class IfParser:
    def __init__(self, parent_parser):
        # Store the parent parser
        self.parser = parent_parser

    def parse(self):
        # Current token is IF, so advance
        self.parser.advance()  # consume 'if'

        # expect '('
        expect_token(self.parser, LmnTokenType.LPAREN, "Expected '(' after 'if'")
        self.parser.advance()  # consume '('

        # parse condition expression
        condition = self.parser.expression_parser.parse_expression()

        # expect ')'
        expect_token(self.parser, LmnTokenType.RPAREN, "Expected ')' after if condition")
        self.parser.advance()  # consume ')'

        # parse then-body until 'else' or 'end'
        then_body = parse_block(self.parser, until_tokens=[LmnTokenType.ELSE, LmnTokenType.END])

        # parse else-body if we see 'else'
        else_body = []
        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.ELSE):
            self.parser.advance()  # consume 'else'
            else_body = parse_block(self.parser, until_tokens=[LmnTokenType.END])

        # expect 'end'
        expect_token(self.parser, LmnTokenType.END, "Expected 'end' after if statement")
        self.parser.advance()  # consume 'end'

        # Return an IfStatement with fields: condition, then_body, else_body
        return IfStatement(
            condition=condition,
            then_body=then_body,
            else_body=else_body
        )

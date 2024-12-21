# compiler/parser/statements/return_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.return_statement import ReturnStatement

class ReturnParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # current_token == RETURN
        self.parser.advance()
        expr = self.parser.expression_parser.parse_expression()
        return ReturnStatement(expr)

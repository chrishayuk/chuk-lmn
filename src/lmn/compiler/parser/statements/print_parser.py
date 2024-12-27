# lmn/compiler/parser/statements/print_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import PrintStatement

class PrintParser:
    def __init__(self, parent_parser):
        # set the parser as the parent parser
        self.parser = parent_parser

    def parse(self):
        # current_token == PRINT, consume
        self.parser.advance()

        # empty list to store the expressions
        expressions = []

        # parse expressions until we see the start of another statement or we reach end/else
        while (
            self.parser.current_token
            and self.parser.current_token.token_type
            not in [
                LmnTokenType.IF,
                LmnTokenType.FOR,
                LmnTokenType.LET,
                LmnTokenType.PRINT,
                LmnTokenType.RETURN,
                LmnTokenType.END,
                LmnTokenType.ELSE,
                LmnTokenType.FUNCTION,
                LmnTokenType.CALL,
            ]
        ):
            # parse the expression
            expr = self.parser.expression_parser.parse_expression()

            # If parse_expression() returned None, break out 
            # (this indicates a statement boundary or invalid expression)
            if expr is None:
                break

            expressions.append(expr)

        return PrintStatement(expressions=expressions)

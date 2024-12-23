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

        # empry list to store the expressions
        expressions = []

        # parse expressions until we see the start of another statement or we reach end/else
        while (
            # check if current token is not None and its type is not one of the following
            self.parser.current_token
            and self.parser.current_token.token_type
            not in [
                LmnTokenType.IF,
                LmnTokenType.FOR,
                LmnTokenType.SET,
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
            expressions.append(expr)

        # 
        return PrintStatement(expressions=expressions)

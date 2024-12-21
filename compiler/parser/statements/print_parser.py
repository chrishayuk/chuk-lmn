# compiler/parser/statements/print_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.statements.print_statement import PrintStatement

class PrintParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # current_token == PRINT, consume
        self.parser.advance()

        expressions = []
        # parse expressions until we see a statement token or end
        while (self.parser.current_token
               and self.parser.current_token.token_type
               not in [LmnTokenType.IF, LmnTokenType.FOR, LmnTokenType.SET,
                       LmnTokenType.PRINT, LmnTokenType.RETURN, LmnTokenType.END,
                       LmnTokenType.ELSE, LmnTokenType.FUNCTION, LmnTokenType.CALL]):
            expr = self.parser.expression_parser.parse_expression()
            expressions.append(expr)

        return PrintStatement(expressions)

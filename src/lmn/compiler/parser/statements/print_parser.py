# lmn/compiler/parser/statements/print_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import PrintStatement
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

class PrintParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        # consume PRINT token
        self.parser.advance()  

        # Parse the expression(s)
        expressions = []

        # Keep parsing expressions until we hit a statement boundary
        while (
            self.parser.current_token
            and not is_statement_boundary(self.parser.current_token.token_type)
        ):
            # Parse the expression
            expr = self.parser.expression_parser.parse_expression()

            # Check for a comma after each expression
            if expr is None:
                break

            # Add the parsed expression to the list of expressions
            expressions.append(expr)

        # return the print statement node
        return PrintStatement(expressions=expressions)
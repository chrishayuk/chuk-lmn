# lmn/compiler/parser/expressions/primary_parser.py

from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)
# Import or define our boundary set
from lmn.compiler.parser.expressions.statement_boundaries import STATEMENT_BOUNDARY_TOKENS

class PrimaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def _skip_comments(self):
        """
        Skip any COMMENT tokens so they never appear as part of an expression.
        """
        while (self.parser.current_token 
               and self.parser.current_token.token_type == LmnTokenType.COMMENT):
            self.parser.advance()

    def parse_primary(self):
        # 1) Skip comment tokens before parsing
        self._skip_comments()

        token = self.parser.current_token

        # 2) If we're out of tokens, that's an error (or 'None' if you prefer)
        if not token:
            raise SyntaxError("Unexpected end of input in primary expression")

        # 3) If this token is a statement boundary, return None
        #    to signal "no valid expression here."
        if token.token_type in STATEMENT_BOUNDARY_TOKENS:
            return None

        ttype = token.token_type

        if ttype == LmnTokenType.NUMBER:
            # 'NUMBER' => parse as LiteralExpression (numeric)
            self.parser.advance()
            return LiteralExpression(value=str(token.value))

        elif ttype == LmnTokenType.STRING:
            # 'STRING' => parse as a string literal
            self.parser.advance()
            return LiteralExpression(value=token.value)

        elif ttype == LmnTokenType.IDENTIFIER:
            # Could be a variable or a function call
            var_name = token.value
            self.parser.advance()  # consume the identifier

            # check if next is '(' => function call
            if (self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.LPAREN):
                self.parser.advance()  # consume '('
                args = []
                # parse arguments until we see ')'
                while (self.parser.current_token
                       and self.parser.current_token.token_type != LmnTokenType.RPAREN):
                    arg_expr = self.expr_parser.parse_expression()
                    args.append(arg_expr)
                    if (self.parser.current_token
                        and self.parser.current_token.token_type == LmnTokenType.COMMA):
                        self.parser.advance()  # consume comma

                self._expect(LmnTokenType.RPAREN, "Expected ')' after function call arguments")
                self.parser.advance()  # consume ')'

                return FnExpression(
                    name=VariableExpression(name=var_name),
                    arguments=args
                )
            else:
                # just a variable
                return VariableExpression(name=var_name)

        elif ttype == LmnTokenType.LPAREN:
            # grouping: ( expr )
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            self._expect(LmnTokenType.RPAREN, "Expected ')' to close grouping")
            self.parser.advance()  # consume ')'
            return expr

        else:
            # If it's not recognized as a valid primary token, raise an error
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def _expect(self, ttype, message):
        """
        Helper to ensure the current token is ttype; otherwise raise SyntaxError.
        """
        if not self.parser.current_token or self.parser.current_token.token_type != ttype:
            raise SyntaxError(message)
        return self.parser.current_token

# lmn/compiler/parser/expressions/primary_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

class PrimaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_primary(self):
        """
        primary := INT_LITERAL
                | LONG_LITERAL
                | FLOAT_LITERAL
                | DOUBLE_LITERAL
                | STRING
                | IDENTIFIER [ '(' args ')' ]
                | '(' expression ')'
        """
        # get the current token
        token = self.parser.current_token

        # If we hit the end of input, raise an error
        if not token:
            # raise the error
            raise SyntaxError("Unexpected end of input in primary expression")

        # If we hit a statement boundary, we're done parsing expressions
        if is_statement_boundary(token.token_type):
            return None
        
        # If we hit a statement boundary, we're done parsing expressions
        ttype = token.token_type

        # Numeric Literals
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL,
        ):
            self.parser.advance()
            return LiteralExpression(value=token.value)

        # String Literals
        if ttype == LmnTokenType.STRING:
            # advance
            self.parser.advance()

            # return the literal expression
            return LiteralExpression(value=token.value)

        # Identifiers (variable or function call)
        if ttype == LmnTokenType.IDENTIFIER:
            var_name = token.value
            self.parser.advance()  # consume identifier

            # Check for function call syntax: name(...)
            if (
                self.parser.current_token 
                and self.parser.current_token.token_type == LmnTokenType.LPAREN
            ):
                self.parser.advance()  # consume '('
                args = []

                # Parse arguments until ')'
                while (
                    self.parser.current_token
                    and self.parser.current_token.token_type != LmnTokenType.RPAREN
                ):
                    arg = self.expr_parser.parse_expression()
                    args.append(arg)

                    # Handle argument separator
                    if (
                        self.parser.current_token
                        and self.parser.current_token.token_type == LmnTokenType.COMMA
                    ):
                        self.parser.advance()  # consume comma

                # Expect closing parenthesis
                self._expect(
                    LmnTokenType.RPAREN,
                    f"Expected ')' after arguments in call to '{var_name}'"
                )
                self.parser.advance()  # consume ')'

                return FnExpression(
                    name=VariableExpression(name=var_name),
                    arguments=args
                )
            
            # Simple variable reference
            return VariableExpression(name=var_name)

        # Parenthesized expression
        if ttype == LmnTokenType.LPAREN:
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            
            self._expect(
                LmnTokenType.RPAREN,
                "Expected ')' to close grouped expression"
            )
            self.parser.advance()  # consume ')'
            
            return expr

        # If we get here, we don't know how to handle this token
        raise SyntaxError(
            f"Unexpected token in primary expression: {token.value} ({token.token_type})"
        )

    def _expect(self, token_type, message):
        """
        Verifies current token is of expected type or raises SyntaxError
        """
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != token_type
        ):
            raise SyntaxError(message)
        return self.parser.current_token
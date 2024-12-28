# lmn/compiler/parser/expressions/primary_parser.py

from lmn.compiler.lexer.token_type import (
    LmnTokenType,
)
from lmn.compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)
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
        """
        primary := INT_LITERAL
                 | LONG_LITERAL
                 | FLOAT_LITERAL
                 | DOUBLE_LITERAL
                 | STRING
                 | IDENTIFIER [ '(' args ')' ]
                 | '(' expression ')'
        """
        # 1) Skip comment tokens before parsing
        self._skip_comments()

        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of input in primary expression")

        # 2) If the token is a statement boundary, return None (no expression found)
        if token.token_type in STATEMENT_BOUNDARY_TOKENS:
            return None

        ttype = token.token_type

        # ------------------
        # Numeric Literals
        # ------------------
        # If the token is one of the new numeric literal types, parse as a literal.
        if ttype in (
            LmnTokenType.INT_LITERAL,
            LmnTokenType.LONG_LITERAL,
            LmnTokenType.FLOAT_LITERAL,
            LmnTokenType.DOUBLE_LITERAL,
        ):
            self.parser.advance()
            # token.value is already the numeric value (int/float) stored by the tokenizer.
            return LiteralExpression(value=token.value)

        # ------------------
        # String Literals
        # ------------------
        elif ttype == LmnTokenType.STRING:
            self.parser.advance()
            return LiteralExpression(value=token.value)

        # ------------------
        # Identifiers (variable or function call)
        # ------------------
        elif ttype == LmnTokenType.IDENTIFIER:
            var_name = token.value
            self.parser.advance()  # consume IDENTIFIER

            # Check if next token is '(' => function call
            if (self.parser.current_token
                and self.parser.current_token.token_type == LmnTokenType.LPAREN):
                # parse function-call syntax: name(...)
                self.parser.advance()  # consume '('
                args = []
                # parse arguments until we see ')'
                while (self.parser.current_token
                       and self.parser.current_token.token_type != LmnTokenType.RPAREN):
                    arg_expr = self.expr_parser.parse_expression()
                    args.append(arg_expr)
                    if (self.parser.current_token
                        and self.parser.current_token.token_type == LmnTokenType.COMMA):
                        self.parser.advance()  # consume ','

                # Expect a closing paren
                self._expect(LmnTokenType.RPAREN, "Expected ')' after function call arguments")
                self.parser.advance()  # consume ')'

                return FnExpression(
                    name=VariableExpression(name=var_name),
                    arguments=args
                )
            else:
                # Just a variable reference
                return VariableExpression(name=var_name)

        # ------------------
        # Parenthesized Expression
        # ------------------
        elif ttype == LmnTokenType.LPAREN:
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            self._expect(LmnTokenType.RPAREN, "Expected ')' to close grouped expression")
            self.parser.advance()  # consume ')'
            return expr

        else:
            # If it's not recognized, raise a syntax error
            raise SyntaxError(f"Unexpected token in primary expression: {token}")

    def _expect(self, ttype, message):
        """
        Helper to ensure the current token is of the specified type, or raise SyntaxError.
        """
        if not self.parser.current_token or self.parser.current_token.token_type != ttype:
            raise SyntaxError(message)
        return self.parser.current_token

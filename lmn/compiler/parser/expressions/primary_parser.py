# compiler/parser/expressions/primary_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast import (
    LiteralExpression,
    FnExpression,
    VariableExpression,
)

class PrimaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_primary(self):
        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of input in primary expression")

        ttype = token.token_type

        if ttype == LmnTokenType.NUMBER:
            # 'NUMBER' => parse as LiteralExpression (numeric)
            self.parser.advance()
            # If the token.value is numeric-like, your LiteralExpression validator
            # will parse it as int or float.
            return LiteralExpression(value=str(token.value))

        elif ttype == LmnTokenType.STRING:
            # 'STRING' => parse as a string literal
            self.parser.advance()
            return LiteralExpression(value=token.value)

        elif ttype == LmnTokenType.IDENTIFIER:
            # Could be a variable or a function call
            var_name = token.value
            self.parser.advance()  # consume the identifier token

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
                        self.parser.advance()  # consume comma, keep parsing args

                # expect ')'
                self._expect(LmnTokenType.RPAREN, "Expected ')' after function call arguments")
                self.parser.advance()  # consume ')'

                # Construct FnExpression with a 'VariableExpression' as the 'name'
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
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def _expect(self, ttype, message):
        if not self.parser.current_token or self.parser.current_token.token_type != ttype:
            raise SyntaxError(message)
        return self.parser.current_token

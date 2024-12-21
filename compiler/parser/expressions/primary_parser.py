# compiler/parser/expressions/primary_parser.py

from compiler.lexer.token_type import LmnTokenType
from compiler.ast.expressions.literal import Literal
from compiler.ast.expressions.fn_expression import FnExpression
from compiler.ast.variable import Variable

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
            self.parser.advance()
            return Literal(str(token.value))

        elif ttype == LmnTokenType.STRING:
            self.parser.advance()
            return Literal(token.value)

        elif ttype == LmnTokenType.IDENTIFIER:
            # Could be var or a function call
            var_name = token.value
            self.parser.advance()

            # check if next is '(' => function call
            if self.parser.current_token and self.parser.current_token.token_type == LmnTokenType.LPAREN:
                self.parser.advance()  # consume '('
                args = []
                while (self.parser.current_token
                       and self.parser.current_token.token_type != LmnTokenType.RPAREN):
                    arg_expr = self.expr_parser.parse_expression()
                    args.append(arg_expr)
                    if (self.parser.current_token
                        and self.parser.current_token.token_type == LmnTokenType.COMMA):
                        self.parser.advance()
                # expect ')'
                self._expect(LmnTokenType.RPAREN, "Expected ')' after function call")
                self.parser.advance()  # consume ')'
                return FnExpression(Variable(var_name), args)
            else:
                # just a variable
                return Variable(var_name)

        elif ttype == LmnTokenType.LPAREN:
            # grouping
            self.parser.advance()  # consume '('
            expr = self.expr_parser.parse_expression()
            self._expect(LmnTokenType.RPAREN, "Expected ')' in grouping")
            self.parser.advance()
            return expr

        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def _expect(self, ttype, message):
        if not self.parser.current_token or self.parser.current_token.token_type != ttype:
            raise SyntaxError(message)
        return self.parser.current_token

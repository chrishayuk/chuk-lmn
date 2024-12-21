# compiler/parser/expressions/binary_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.expressions.binary_expression import BinaryExpression

class BinaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_binary_expr(self):
        """
        Example approach:
          left = parse_unary_expr
          while current_token is a binary operator:
            op_token = current_token
            advance()
            right = parse_unary_expr
            left = BinaryExpression(left, op_token, right)
          return left
        """
        left = self.expr_parser.parse_unary_expr()

        while self._is_binary_operator(self.parser.current_token):
            op_token = self.parser.current_token
            self.parser.advance()
            right = self.expr_parser.parse_unary_expr()
            left = BinaryExpression(left, op_token, right)

        return left

    def _is_binary_operator(self, token):
        if not token:
            return False
        return token.token_type in [
            LmnTokenType.PLUS, LmnTokenType.MINUS, LmnTokenType.MUL, LmnTokenType.DIV,
            LmnTokenType.EQ, LmnTokenType.NE, LmnTokenType.LT, LmnTokenType.LE,
            LmnTokenType.GT, LmnTokenType.GE, LmnTokenType.AND, LmnTokenType.OR
        ]

# lmn/compiler/parser/expressions/binary_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import BinaryExpression

class BinaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_binary_expr(self):
        """
        Example approach:
          left = parse_unary_expr()
          while current_token is a binary operator:
              op_token = current_token
              advance()
              right = parse_unary_expr()
              left = BinaryExpression(operator=op_token.value, left=left, right=right)
          return left
        """
        left = self.expr_parser.parse_unary_expr()

        while self._is_binary_operator(self.parser.current_token):
            op_token = self.parser.current_token
            self.parser.advance()

            right = self.expr_parser.parse_unary_expr()

            # old code was: left = BinaryExpression(left, op_token, right)
            # new approach uses named fields => 'operator=op_token.value'
            left = BinaryExpression(
                operator=op_token.value,  # or op_token.lexeme if that's how you store it
                left=left,
                right=right
            )

        return left

    def _is_binary_operator(self, token):
        if not token:
            return False

        # Distinguish assignment (=) from comparison (==)
        # by including EQEQ for equality comparison.
        return token.token_type in [
            LmnTokenType.PLUS, 
            LmnTokenType.MINUS, 
            LmnTokenType.MUL, 
            LmnTokenType.DIV,
            LmnTokenType.EQEQ,   # <-- Add '==' for equality
            LmnTokenType.NE, 
            LmnTokenType.LT, 
            LmnTokenType.LE,
            LmnTokenType.GT, 
            LmnTokenType.GE, 
            LmnTokenType.AND, 
            LmnTokenType.OR
        ]


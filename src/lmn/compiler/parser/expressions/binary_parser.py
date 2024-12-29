# file: lmn/compiler/parser/expressions/binary_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.expressions.operator_precedence import OP_PRECEDENCE
from lmn.compiler.ast import BinaryExpression

class BinaryParser:
    def __init__(self, parent_parser, expr_parser):
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_binary_expr(self, min_prec=0):
        """
        Precedence-climbing approach:
          1) Parse left side as a unary_expr
          2) While the next token is a binary operator with precedence >= min_prec:
               - consume operator
               - parse right side at higher precedence (op_prec + 1) for left-associative
                 or at the same precedence for right-associative
               - combine into BinaryExpression
          3) Return the final 'left' expression
        """
        left = self.expr_parser.parse_unary_expr()

        while True:
            token = self.parser.current_token
            if not token or token.token_type not in OP_PRECEDENCE:
                break

            op_prec = OP_PRECEDENCE[token.token_type]
            if op_prec < min_prec:
                break

            # This operator is valid at this precedence level, so consume it
            op_token = token
            self.parser.advance()

            # By default, left-associative => parse right with op_prec + 1
            next_min_prec = op_prec + 1

            right = self.parse_binary_expr(min_prec=next_min_prec)

            # Build the binary expression node
            left = BinaryExpression(
                operator=op_token.value,
                left=left,
                right=right
            )

        return left
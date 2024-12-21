# compiler/parser/expressions/unary_parser.py
from compiler.lexer.token_type import LmnTokenType
from compiler.ast.expressions.unary_expression import UnaryExpression

class UnaryParser:
    def __init__(self, parent_parser, expr_parser):
        """
        parent_parser = the main Parser object
        expr_parser   = the ExpressionParser instance
        """
        self.parser = parent_parser
        self.expr_parser = expr_parser

    def parse_unary_expr(self):
        """
        unary := ("+"|"-"|"not") unary | primary
        """
        token = self.parser.current_token
        if token and token.token_type in [LmnTokenType.PLUS, LmnTokenType.MINUS, LmnTokenType.NOT]:
            op_token = token
            self.parser.advance()
            operand = self.parse_unary_expr()  # recursive
            return UnaryExpression(op_token, operand)
        else:
            # fallback to primary
            return self.expr_parser.parse_primary()

# lmn/compiler/parser/expressions/unary_parser.py
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import UnaryExpression, PostfixExpression

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
        unary := (PLUS | MINUS | NOT) unary | postfix
        """
        token = self.parser.current_token

        # 1) Check for prefix operators: +, -, not
        if token and token.token_type in [LmnTokenType.PLUS,
                                          LmnTokenType.MINUS,
                                          LmnTokenType.NOT]:
            op_token = token
            self.parser.advance()  # consume the prefix operator

            operand = self.parse_unary_expr()  # parse next unary expr
            return UnaryExpression(
                operator=op_token.value,
                operand=operand
            )
        
        # 2) Otherwise, parse a "postfix" expression
        return self.parse_postfix_expr()

    def parse_postfix_expr(self):
        """
        postfix := primary { INC | DEC }
        
        1. Parse a primary expression (literal, variable, function call, etc.)
        2. While the next token is ++ or --, build a PostfixExpression node.
        """
        expr = self.expr_parser.parse_primary()

        # Loop to handle multiple postfix ops, e.g. a++-- is unusual but possible
        while (self.parser.current_token and
               self.parser.current_token.token_type in (LmnTokenType.INC, LmnTokenType.DEC)):

            op_token = self.parser.current_token
            self.parser.advance()  # consume ++ or --
            
            # Build a PostfixExpression node
            expr = PostfixExpression(
                operator=op_token.value,  # '++' or '--'
                operand=expr
            )

        return expr

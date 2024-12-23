# compiler/parser/expressions/expression_parser.py
from compiler.parser.expressions.unary_parser import UnaryParser
from compiler.parser.expressions.binary_parser import BinaryParser
from compiler.parser.expressions.primary_parser import PrimaryParser
from compiler.lexer.token_type import LmnTokenType

class ExpressionParser:
    """
    Coordinates different expression sub-parsers:
      - parse_expression() might handle the overall grammar or precedence
      - parse_binary_expr() defers to BinaryParser
      - parse_unary_expr() defers to UnaryParser
      - parse_primary() defers to PrimaryParser, etc.
    """
    def __init__(self, parent_parser):
        self.parser = parent_parser
        # Each sub-parser will handle its own logic (binary, unary, primary).
        # They rely on self (ExpressionParser) for sub-calls, e.g. parse_unary_expr().
        self.binary_parser = BinaryParser(self.parser, self)
        self.unary_parser = UnaryParser(self.parser, self)
        self.primary_parser = PrimaryParser(self.parser, self)

    def parse_expression(self):
        """
        Entry point for expression parsing.
        For a simplified approach, we parse a binary expression from the start.
        """
        return self.parse_binary_expr()

    def parse_binary_expr(self, prec=0):
        """
        Defer to the BinaryParser for handling operator precedence and
        constructing a BinaryExpression node.
        """
        return self.binary_parser.parse_binary_expr()

    def parse_unary_expr(self):
        """
        Defer to the UnaryParser. E.g. handle prefix operators like - or not.
        """
        return self.unary_parser.parse_unary_expr()

    def parse_primary(self):
        """
        Defer to the PrimaryParser for literals, variables, grouping parentheses, etc.
        """
        return self.primary_parser.parse_primary()

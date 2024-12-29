# lmn/compiler/parser/expressions/expression_parser.py

from lmn.compiler.parser.expressions.unary_parser import UnaryParser
from lmn.compiler.parser.expressions.binary_parser import BinaryParser
from lmn.compiler.parser.expressions.primary_parser import PrimaryParser
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.statements.statement_boundaries import STATEMENT_BOUNDARY_TOKENS

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
        self.binary_parser = BinaryParser(self.parser, self)
        self.unary_parser = UnaryParser(self.parser, self)
        self.primary_parser = PrimaryParser(self.parser, self)

    def _skip_comments(self):
        """
        Helper method to skip any COMMENT tokens in the current token stream.
        """
        while (self.parser.current_token
               and self.parser.current_token.token_type == LmnTokenType.COMMENT):
            self.parser.advance()

    def _is_statement_boundary(self):
        """
        Check if the current token is one of the statement boundary tokens.
        """
        token = self.parser.current_token
        return (token is None 
                or token.token_type in STATEMENT_BOUNDARY_TOKENS)

    def parse_expression(self):
        """
        Entry point for expression parsing.
        If we see a statement boundary token, return None immediately
        (meaning "no expression here").
        """
        self._skip_comments()

        # If the current token is a statement boundary, return None
        if self._is_statement_boundary():
            return None

        return self.parse_binary_expr()

    def parse_binary_expr(self, prec=0):
        """
        Defer to the BinaryParser for handling operator precedence and
        constructing a BinaryExpression node.
        """
        self._skip_comments()

        # If next token is a statement boundary, return None
        if self._is_statement_boundary():
            return None

        return self.binary_parser.parse_binary_expr()

    def parse_unary_expr(self):
        """
        Defer to the UnaryParser. E.g. handle prefix operators like - or not.
        """
        self._skip_comments()

        # If next token is a statement boundary, return None
        if self._is_statement_boundary():
            return None

        return self.unary_parser.parse_unary_expr()

    def parse_primary(self):
        """
        Defer to the PrimaryParser for literals, variables, grouping parentheses, etc.
        """
        self._skip_comments()

        # If next token is a statement boundary, return None
        if self._is_statement_boundary():
            return None

        return self.primary_parser.parse_primary()

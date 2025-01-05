# file: lmn/compiler/parser/expressions/expression_parser.py

import logging

from lmn.compiler.parser.expressions.function_expression_parser import FunctionExpressionParser
from lmn.compiler.parser.expressions.unary_parser import UnaryParser
from lmn.compiler.parser.expressions.binary_parser import BinaryParser
from lmn.compiler.parser.expressions.primary_parser import PrimaryParser

# Instead of referencing STATEMENT_BOUNDARY_TOKENS directly,
# we import is_statement_boundary for two-mode handling (expression vs. statement).
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

from lmn.compiler.lexer.token_type import LmnTokenType

# logger
logger = logging.getLogger(__name__)

class ExpressionParser:
    """
    Coordinates different expression sub-parsers:
      - parse_expression() handles the overall grammar or precedence
      - parse_assignment_expr() handles assignment operators (if allowed in expressions)
      - parse_binary_expr() defers to BinaryParser (now with precedence climbing)
      - parse_unary_expr()  defers to UnaryParser
      - parse_primary()     defers to PrimaryParser
    """
    def __init__(self, parent_parser):
        self.parser = parent_parser
        self.binary_parser = BinaryParser(self.parser, self)
        self.unary_parser = UnaryParser(self.parser, self)
        self.primary_parser = PrimaryParser(self.parser, self)

        # Instantiate your existing FunctionExpressionParser
        self.function_expression_parser = FunctionExpressionParser(self.parser, self)

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
        However, for expression context, we exclude 'function' from the set
        so inline function definitions are allowed (e.g., let sum_func = function(...) ... end).
        """
        token = self.parser.current_token
        if not token:
            return True

        # Use in_expression=True => 'function' won't terminate expression parsing
        return is_statement_boundary(token.token_type, in_expression=True)

    # -------------------------------------------------------------------------
    # (1) parse_expression: top-level entry point for expressions
    # -------------------------------------------------------------------------
    def parse_expression(self):
        """
        If we see a statement boundary token, return None immediately.
        Otherwise, parse an expression (including possible assignments).
        """
        self._skip_comments()
        if self._is_statement_boundary():
            return None

        return self.parse_assignment_expr()

    # -------------------------------------------------------------------------
    # (2) parse_assignment_expr: handles =, +=, -=, =+, =-, etc.
    # -------------------------------------------------------------------------
    def parse_assignment_expr(self):
        """
        assignment_expr:
          left_expr = parse_binary_expr()
          if next token is assignment op (e.g. =, +=, -=, =+, =-),
             consume it
             right_expr = parse_assignment_expr()   # recursion for chaining
             build AssignmentExpression node
          else
             return left_expr
        """

        # First parse the left side as a normal binary expression
        left_expr = self.parse_binary_expr()

        # Check if the current token is an assignment operator
        current = self.parser.current_token
        if current and current.token_type in (
            LmnTokenType.EQ,
            LmnTokenType.PLUS_EQ,
            LmnTokenType.MINUS_EQ,
            LmnTokenType.EQ_PLUS,
            LmnTokenType.EQ_MINUS,
        ):
            op_token = current
            self.parser.advance()  # consume the operator

            # parse the right side as assignment_expr (allowing chaining, e.g. a = b = c)
            right_expr = self.parse_assignment_expr()

            return self._build_assignment_expr(left_expr, op_token, right_expr)

        # If no assignment operator, just return the binary expression
        return left_expr

    def _build_assignment_expr(self, left_expr, op_token, right_expr):
        """
        Convert compound assignment into a normal assignment with a BinaryExpression
        if necessary.
          a += b => a = a + b
          a =+ b => a = a + b
          ...
        """
        if op_token.token_type == LmnTokenType.EQ:
            # a = b
            return self._build_assignment_node(left_expr, right_expr)

        elif op_token.token_type == LmnTokenType.PLUS_EQ:
            # a += b => a = a + b
            plus_expr = self._build_binary_node(
                operator='+',
                left_expr=left_expr,
                right_expr=right_expr
            )
            return self._build_assignment_node(left_expr, plus_expr)

        elif op_token.token_type == LmnTokenType.MINUS_EQ:
            # a -= b => a = a - b
            minus_expr = self._build_binary_node(
                operator='-',
                left_expr=left_expr,
                right_expr=right_expr
            )
            return self._build_assignment_node(left_expr, minus_expr)

        elif op_token.token_type == LmnTokenType.EQ_PLUS:
            # a =+ b => a = a + b
            plus_expr = self._build_binary_node(
                operator='+',
                left_expr=left_expr,
                right_expr=right_expr
            )
            return self._build_assignment_node(left_expr, plus_expr)

        elif op_token.token_type == LmnTokenType.EQ_MINUS:
            # a =- b => a = a - b
            minus_expr = self._build_binary_node(
                operator='-',
                left_expr=left_expr,
                right_expr=right_expr
            )
            return self._build_assignment_node(left_expr, minus_expr)

        raise SyntaxError(f"Unhandled assignment operator: {op_token.value}")

    def _build_assignment_node(self, left_expr, right_expr):
        """
        Build an AssignmentExpression node (Pydantic-based) with keyword args.
        """
        from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
        return AssignmentExpression(left=left_expr, right=right_expr)

    def _build_binary_node(self, operator, left_expr, right_expr):
        """
        Build a BinaryExpression node with keyword arguments.
        """
        from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
        return BinaryExpression(operator=operator, left=left_expr, right=right_expr)

    # -------------------------------------------------------------------------
    # (3) parse_binary_expr: defers to BinaryParser, supports multi-level precedence
    # -------------------------------------------------------------------------
    def parse_binary_expr(self, prec=0):
        """
        Defer to the BinaryParser for precedence among +, -, *, /, //, %, etc.
        We pass min_prec=0 by default, but you can adjust if needed.
        """
        # skip comments
        self._skip_comments()

        # check if there is a statement boundary
        if self._is_statement_boundary():
            return None

        # parse binary expression
        return self.binary_parser.parse_binary_expr(min_prec=prec)

    # -------------------------------------------------------------------------
    # (4) parse_unary_expr: defers to UnaryParser for prefix ops
    # -------------------------------------------------------------------------
    def parse_unary_expr(self):
        # skip comments
        self._skip_comments()

        # check if there is a statement boundary
        if self._is_statement_boundary():
            return None
        
        # Check if it's an inline function
        logger.debug("parse_unary_expr sees token: %s", self.parser.current_token)
        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.FUNCTION):

            # Delegate parsing to your existing FunctionExpressionParser
            logger.debug("parse_unary_expr calling parse_function_expression()")
            func_exp = self.function_expression_parser.parse_function_expression()
            logger.info(f"parse_unary_expr received from parse_function_expression(): {func_exp}")
            # to dict
            logger.info(func_exp.to_dict())

            # return the expression
            return func_exp
        
        # parse unary expression
        return self.unary_parser.parse_unary_expr()

    # -------------------------------------------------------------------------
    # (5) parse_primary: defers to PrimaryParser for literals, variables, etc.
    # -------------------------------------------------------------------------
    def parse_primary(self):
        # skip comments
        self._skip_comments()

        # check if there is a statement boundary
        if self._is_statement_boundary():
            return None
        
        # parse primary
        return self.primary_parser.parse_primary()

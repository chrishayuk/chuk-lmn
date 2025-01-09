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
            logger.debug("ExpressionParser: Skipping comment: %r", self.parser.current_token.value)
            self.parser.advance()

    def _is_statement_boundary(self):
        """
        Check if the current token is one of the statement boundary tokens.
        However, for expression context, we exclude 'function' from the set
        so inline function definitions are allowed (e.g., let sum_func = function(...) ... end).
        """
        token = self.parser.current_token
        if not token:
            logger.debug("ExpressionParser: No current token => statement boundary.")
            return True

        boundary = is_statement_boundary(token.token_type, in_expression=True)
        logger.debug("ExpressionParser: Checking boundary for token %r => %s", token, boundary)
        return boundary

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
            logger.debug("ExpressionParser.parse_expression: Statement boundary reached. Returning None.")
            return None

        logger.debug("ExpressionParser.parse_expression: Starting parse_assignment_expr.")
        expr = self.parse_assignment_expr()
        logger.debug("ExpressionParser.parse_expression: Finished => %r", expr)
        return expr

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

        logger.debug("ExpressionParser.parse_assignment_expr: Parsing left side (binary_expr).")
        left_expr = self.parse_binary_expr()

        current = self.parser.current_token
        if current and current.token_type in (
            LmnTokenType.EQ,
            LmnTokenType.PLUS_EQ,
            LmnTokenType.MINUS_EQ,
            LmnTokenType.EQ_PLUS,
            LmnTokenType.EQ_MINUS,
        ):
            logger.debug("ExpressionParser.parse_assignment_expr: Detected assignment operator %r", current.value)
            op_token = current
            self.parser.advance()  # consume the operator

            logger.debug("ExpressionParser.parse_assignment_expr: Parsing right side (assignment_expr).")
            right_expr = self.parse_assignment_expr()

            assignment_expr = self._build_assignment_expr(left_expr, op_token, right_expr)
            logger.debug("ExpressionParser.parse_assignment_expr: Built assignment => %r", assignment_expr)
            return assignment_expr

        logger.debug("ExpressionParser.parse_assignment_expr: No assignment operator. Returning => %r", left_expr)
        return left_expr

    def _build_assignment_expr(self, left_expr, op_token, right_expr):
        """
        Convert compound assignment into a normal assignment with a BinaryExpression
        if necessary.
          a += b => a = a + b
          a =+ b => a = a + b
          ...
        """
        logger.debug("ExpressionParser._build_assignment_expr: left=%r, operator=%r, right=%r",
                     left_expr, op_token.value, right_expr)

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
        logger.debug("ExpressionParser._build_assignment_node: Creating AssignmentExpression node.")
        return AssignmentExpression(left=left_expr, right=right_expr)

    def _build_binary_node(self, operator, left_expr, right_expr):
        """
        Build a BinaryExpression node with keyword arguments.
        """
        from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
        logger.debug("ExpressionParser._build_binary_node: Creating BinaryExpression with operator=%r", operator)
        return BinaryExpression(operator=operator, left=left_expr, right=right_expr)

    # -------------------------------------------------------------------------
    # (3) parse_binary_expr: defers to BinaryParser, supports multi-level precedence
    # -------------------------------------------------------------------------
    def parse_binary_expr(self, prec=0):
        """
        Defer to the BinaryParser for precedence among +, -, *, /, //, %, etc.
        We pass min_prec=0 by default, but you can adjust if needed.
        """
        self._skip_comments()

        if self._is_statement_boundary():
            logger.debug("ExpressionParser.parse_binary_expr: Statement boundary => returning None")
            return None

        logger.debug("ExpressionParser.parse_binary_expr: Delegating to BinaryParser with min_prec=%d", prec)
        expr = self.binary_parser.parse_binary_expr(min_prec=prec)
        logger.debug("ExpressionParser.parse_binary_expr: Received binary expr => %r", expr)
        return expr

    # -------------------------------------------------------------------------
    # (4) parse_unary_expr: defers to UnaryParser for prefix ops
    # -------------------------------------------------------------------------
    def parse_unary_expr(self):
        self._skip_comments()

        if self._is_statement_boundary():
            logger.debug("ExpressionParser.parse_unary_expr: Statement boundary => returning None")
            return None
        
        logger.debug("ExpressionParser.parse_unary_expr: Current token => %r", self.parser.current_token)
        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.FUNCTION):
            # Delegate parsing to your existing FunctionExpressionParser
            logger.debug("ExpressionParser.parse_unary_expr: Detected 'function'. Delegating to FunctionExpressionParser.")
            func_exp = self.function_expression_parser.parse_function_expression()
            logger.info("ExpressionParser.parse_unary_expr: Received from parse_function_expression => %r", func_exp)
            logger.info(func_exp.to_dict())  # optional: logs a dict representation
            return func_exp
        
        unary = self.unary_parser.parse_unary_expr()
        logger.debug("ExpressionParser.parse_unary_expr: unary_parser returned => %r", unary)
        return unary

    # -------------------------------------------------------------------------
    # (5) parse_primary: defers to PrimaryParser for literals, variables, etc.
    # -------------------------------------------------------------------------
    def parse_primary(self):
        self._skip_comments()

        if self._is_statement_boundary():
            logger.debug("ExpressionParser.parse_primary: Statement boundary => returning None")
            return None
        
        logger.debug("ExpressionParser.parse_primary: Delegating to PrimaryParser.")
        primary_expr = self.primary_parser.parse_primary()
        logger.debug("ExpressionParser.parse_primary: PrimaryParser returned => %r", primary_expr)
        return primary_expr

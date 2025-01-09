# file: lmn/compiler/parser/statements/assignment_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token
from lmn.compiler.ast.statements.assignment_statement import AssignmentStatement
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression

logger = logging.getLogger(__name__)

class AssignmentParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parse an assignment statement of form:
            myVar = expression
            myVar += expression
            myVar -= expression
            etc.
        """
        logger.debug("AssignmentParser: Starting to parse an assignment statement.")

        # 1) Expect an IDENTIFIER for the variable name
        logger.debug("AssignmentParser: Expecting variable name (IDENTIFIER).")
        var_token = expect_token(
            self.parser,
            LmnTokenType.IDENTIFIER,
            "Expected variable name for assignment"
        )
        var_name = var_token.value
        logger.debug("AssignmentParser: Found variable name '%s'.", var_name)
        self.parser.advance()  # consume the identifier

        # 2) Check if the next token is =, +=, -=, etc.
        op_token = self.parser.current_token
        if not op_token:
            logger.error("AssignmentParser: Missing assignment operator after variable name '%s'.", var_name)
            raise SyntaxError("Expected assignment operator after variable name")

        valid_ops = (
            LmnTokenType.EQ,       # =
            LmnTokenType.PLUS_EQ,  # +=
            LmnTokenType.MINUS_EQ, # -=
        )
        if op_token.token_type not in valid_ops:
            logger.error("AssignmentParser: Unexpected assignment operator '%s'.", op_token.value)
            raise SyntaxError(f"Unexpected assignment operator: {op_token.value}")

        logger.debug("AssignmentParser: Detected operator '%s'.", op_token.value)
        self.parser.advance()  # consume the assignment operator

        # 3) Parse right-hand side expression
        logger.debug("AssignmentParser: Parsing right-hand side expression.")
        rhs_expr = self.parser.expression_parser.parse_expression()
        if rhs_expr is None:
            logger.error("AssignmentParser: Missing expression after operator '%s'.", op_token.value)
            raise SyntaxError("Expected expression after assignment operator")

        # 4) Build and return the AssignmentStatement node
        logger.debug("AssignmentParser: Building assignment statement for operator '%s'.", op_token.value)
        if op_token.token_type == LmnTokenType.EQ:
            # direct assignment
            stmt = AssignmentStatement(variable_name=var_name, expression=rhs_expr)
            logger.debug("AssignmentParser: Created AssignmentStatement => %s", stmt)
            return stmt

        elif op_token.token_type == LmnTokenType.PLUS_EQ:
            # a += b => a = a + b
            plus_expr = BinaryExpression(
                operator='+',
                left=VariableExpression(name=var_name),
                right=rhs_expr
            )
            stmt = AssignmentStatement(variable_name=var_name, expression=plus_expr)
            logger.debug("AssignmentParser: Created compound '+=' assignment => %s", stmt)
            return stmt

        elif op_token.token_type == LmnTokenType.MINUS_EQ:
            # a -= b => a = a - b
            minus_expr = BinaryExpression(
                operator='-',
                left=VariableExpression(name=var_name),
                right=rhs_expr
            )
            stmt = AssignmentStatement(variable_name=var_name, expression=minus_expr)
            logger.debug("AssignmentParser: Created compound '-=' assignment => %s", stmt)
            return stmt

        # If you support more compound ops, handle them similarly
        logger.error("AssignmentParser: Unhandled assignment operator '%s'.", op_token.value)
        raise SyntaxError(f"Unhandled assignment operator: {op_token.value}")

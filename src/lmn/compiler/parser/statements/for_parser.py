from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.statements.for_statement import ForStatement
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.parser.parser_utils import expect_token, parse_block
import logging

logger = logging.getLogger(__name__)

class ForParser:
    def __init__(self, parent_parser):
        """
        Initializes the ForParser with a reference to the main parser.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses a 'for' loop statement.
        Supports two forms:
        1. for i = start_expr to end_expr
        2. for i in collection
        """
        logger.debug("ForParser: Starting to parse 'for' loop")

        # 1) Consume 'for'
        token = self.parser.current_token
        logger.debug(f"ForParser: Consuming 'for' token: {token}")
        self.parser.advance()

        # 2) Expect a loop variable (identifier)
        var_token = expect_token(
            self.parser, 
            LmnTokenType.IDENTIFIER, 
            "Expected loop variable after 'for'"
        )
        logger.debug(f"ForParser: Found loop variable '{var_token.value}'")
        loop_var = VariableExpression(name=var_token.value)
        self.parser.advance()  # consume the identifier token

        # 3) Check for 'in' or '='
        start_expr, end_expr = None, None
        if (self.parser.current_token 
            and self.parser.current_token.token_type == LmnTokenType.IN):
            # for i in collection
            logger.debug("ForParser: Detected 'in' syntax for collection iteration")
            self.parser.advance()  # consume 'in'
            start_expr = self.parser.expression_parser.parse_expression()
            logger.debug(f"ForParser: Parsed collection expression => {start_expr}")
        else:
            # for i = start_expr to end_expr
            logger.debug("ForParser: Detected 'start_expr to end_expr' range syntax")
            expect_token(self.parser, LmnTokenType.EQ, "Expected '=' after loop variable")
            self.parser.advance()  # consume '='
            start_expr = self.parser.expression_parser.parse_expression()
            logger.debug(f"ForParser: Parsed start expression => {start_expr}")

            expect_token(self.parser, LmnTokenType.TO, "Expected 'to' after start expression in for-range")
            self.parser.advance()  # consume 'to'
            end_expr = self.parser.expression_parser.parse_expression()
            logger.debug(f"ForParser: Parsed end expression => {end_expr}")

        # 4) Parse the loop body
        logger.debug("ForParser: Entering loop block")
        self.parser.in_loop_context = True  # mark that we're inside a loop
        try:
            body = parse_block(self.parser, until_tokens=[LmnTokenType.END])
            logger.debug(f"ForParser: Parsed loop body => {body}")
        finally:
            self.parser.in_loop_context = False  # exit loop context

        # 5) Ensure we find 'end' after the loop block
        expect_token(self.parser, LmnTokenType.END, "Expected 'end' after for block")
        self.parser.advance()  # consume 'end'
        logger.debug("ForParser: Found 'end' token, completing 'for' loop")

        # 6) Construct and return a ForStatement
        for_statement = ForStatement(
            variable=loop_var,
            start_expr=start_expr,
            end_expr=end_expr,
            step_expr=None,  # Step expression is not currently supported
            body=body
        )
        logger.debug(f"ForParser: Constructed ForStatement => {for_statement}")

        return for_statement

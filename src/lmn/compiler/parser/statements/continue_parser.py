# file: lmn/compiler/parser/statements/continue_parser.py

import logging
from lmn.compiler.ast.statements.continue_statement import ContinueStatement
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token

logger = logging.getLogger(__name__)

class ContinueParser:
    def __init__(self, parent_parser):
        """
        Initializes the ContinueParser with a reference to the main parser.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses a 'continue' statement.
        Ensures the 'continue' is used only within a loop context.
        """
        logger.debug("ContinueParser: Starting to parse 'continue' statement")

        # Check if 'continue' is used in a valid loop context
        if not self.parser.in_loop_context:
            logger.error("ContinueParser: 'continue' used outside of a loop")
            raise SyntaxError("'continue' used outside of a loop")

        # Expect and consume the 'continue' token
        token = self.parser.current_token
        logger.debug("ContinueParser: Current token => %r", token)
        expect_token(self.parser, LmnTokenType.CONTINUE, "Expected 'continue'")

        self.parser.advance()  # consume 'continue'
        logger.debug("ContinueParser: Successfully consumed 'continue' token")

        # Return the AST node for the 'continue' statement
        continue_statement = ContinueStatement()
        logger.debug("ContinueParser: Created ContinueStatement => %r", continue_statement)

        return continue_statement

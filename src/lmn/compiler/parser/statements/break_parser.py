from lmn.compiler.ast.statements.break_statement import BreakStatement
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.parser_utils import expect_token
import logging

logger = logging.getLogger(__name__)

class BreakParser:
    def __init__(self, parent_parser):
        """
        Initializes the BreakParser with a reference to the main parser.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses a 'break' statement.
        Ensures the 'break' is used only within a loop context.
        """
        logger.debug("BreakParser: Starting to parse 'break' statement")

        # 1) Verify the loop context
        if not self.parser.in_loop_context:
            logger.error("BreakParser: 'break' used outside of a loop context")
            raise SyntaxError("'break' used outside of a loop")

        # 2) Expect and consume the 'break' token
        token = self.parser.current_token
        logger.debug("BreakParser: Current token => %r", token)
        expect_token(self.parser, LmnTokenType.BREAK, "Expected 'break'")

        self.parser.advance()  # consume 'break'
        logger.debug("BreakParser: Successfully consumed 'break' token")

        # 3) Create and return the AST node for 'break'
        break_stmt = BreakStatement()
        logger.debug("BreakParser: Created BreakStatement => %r", break_stmt)

        return break_stmt

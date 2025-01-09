# file: lmn/compiler/parser/statements/statement_parser.py

from typing import Optional
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.statements.assignment_parser import AssignmentParser
from lmn.compiler.parser.statements.block_parser import BlockParser
from lmn.compiler.parser.statements.break_parser import BreakParser
from lmn.compiler.parser.statements.continue_parser import ContinueParser
from lmn.compiler.parser.statements.function_call_parser import FunctionCallParser
from lmn.compiler.parser.statements.function_definition_parser import FunctionDefinitionParser
from lmn.compiler.parser.statements.if_parser import IfParser
from lmn.compiler.parser.statements.for_parser import ForParser
from lmn.compiler.parser.statements.let_parser import LetParser
from lmn.compiler.parser.statements.print_parser import PrintParser
from lmn.compiler.parser.statements.return_parser import ReturnParser
# If you have a dedicated function-call statement parser:
# from lmn.compiler.parser.statements.fn_call_parser import FnCallParser 

import logging
logger = logging.getLogger(__name__)

class StatementParser:
    def __init__(self, parent_parser):
        """
        :param parent_parser: reference to the main Parser instance
        """
        self.parser = parent_parser

    def parse_statement(self):
        """
        Attempts to parse a single statement based on the current token type.

        - function -> FunctionDefinitionParser
        - identifier -> (function call) or (assignment)
        - if -> IfParser
        - for -> ForParser
        - let -> LetParser
        - print -> PrintParser
        - return -> ReturnParser
        - begin -> BlockParser
        - otherwise -> SyntaxError
        """

        # 1) Skip any COMMENT or NEWLINE tokens
        while (
            self.parser.current_token
            and self.parser.current_token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE)
        ):
            logger.debug(
                "StatementParser: Skipping %s token => %r",
                self.parser.current_token.token_type.name,
                self.parser.current_token.value
            )
            self.parser.advance()

        token = self.parser.current_token

        # If no token remains
        if token is None:
            logger.debug("StatementParser: No more tokens; returning None.")
            return None

        ttype = token.token_type
        logger.debug("StatementParser: next statement token_type=%s", ttype.name)

        # 2) Dispatch based on the token type
        if ttype == LmnTokenType.FUNCTION:
            logger.debug("StatementParser: Handling 'function' definition.")
            self.parser.advance()
            return FunctionDefinitionParser(self.parser).parse()

        elif ttype == LmnTokenType.IDENTIFIER:
            # We need to check if it's a function call or an assignment
            next_token = self.parser.peek(1)  # peek one token ahead
            if next_token and next_token.token_type == LmnTokenType.LPAREN:
                # We have a function call statement
                logger.debug("StatementParser: Handling function call with IDENTIFIER => %r", token.value)
                self.parser.advance()  # consume the IDENTIFIER
                fn_name = token.value

                # parse the call
                call_stmt = FunctionCallParser(self.parser, fn_name).parse()
                return call_stmt
            else:
                # It's an assignment statement
                logger.debug("StatementParser: Handling assignment with IDENTIFIER => %r", token.value)
                return AssignmentParser(self.parser).parse()

        elif ttype == LmnTokenType.IF:
            logger.debug("StatementParser: Handling 'if' statement.")
            return IfParser(self.parser).parse()

        elif ttype == LmnTokenType.FOR:
            logger.debug("StatementParser: Handling 'for' loop.")
            return ForParser(self.parser).parse()

        elif ttype == LmnTokenType.BREAK:
            logger.debug("StatementParser: 'break' token encountered.")
            return BreakParser(self.parser).parse()

        elif ttype == LmnTokenType.CONTINUE:
            logger.debug("StatementParser: 'continue' token encountered.")
            return ContinueParser(self.parser).parse()

        elif ttype == LmnTokenType.LET:
            logger.debug("StatementParser: Handling 'let' statement.")
            return LetParser(self.parser).parse()

        elif ttype == LmnTokenType.PRINT:
            logger.debug("StatementParser: Handling 'print' statement.")
            return PrintParser(self.parser).parse()

        elif ttype == LmnTokenType.RETURN:
            logger.debug("StatementParser: Handling 'return' statement.")
            return ReturnParser(self.parser).parse()

        elif ttype == LmnTokenType.BEGIN:
            logger.debug("StatementParser: Handling 'begin' block.")
            return BlockParser(self.parser).parse()

        # 4) If none matched, error
        logger.debug("StatementParser: Found unrecognized token for statement => %s", ttype.name)
        raise SyntaxError(f"Unexpected token for statement: {ttype}")

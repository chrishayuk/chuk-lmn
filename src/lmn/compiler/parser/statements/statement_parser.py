# file: lmn/compiler/parser/statements/statement_parser.py
from typing import Optional
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.parser.statements.assignment_parser import AssignmentParser
from lmn.compiler.parser.statements.block_parser import BlockParser
from lmn.compiler.parser.statements.function_definition_parser import FunctionDefinitionParser
from lmn.compiler.parser.statements.if_parser import IfParser
from lmn.compiler.parser.statements.for_parser import ForParser
from lmn.compiler.parser.statements.let_parser import LetParser
from lmn.compiler.parser.statements.print_parser import PrintParser
from lmn.compiler.parser.statements.return_parser import ReturnParser

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
        - identifier -> AssignmentParser
        - if -> IfParser
        - for -> ForParser
        - let -> LetParser
        - print -> PrintParser
        - return -> ReturnParser
        - begin -> BlockParser
        - otherwise -> SyntaxError
        """

        # 1) Skip any COMMENT or NEWLINE tokens *before* we do anything else.
        while (
            self.parser.current_token 
            and self.parser.current_token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE)
        ):
            logger.debug(
                "parse_statement: skipping %s token: %r",
                self.parser.current_token.token_type.name,
                self.parser.current_token.value
            )
            self.parser.advance()

        token = self.parser.current_token

        # If we've run out of tokens after skipping
        if token is None:
            return None
        
        ttype = token.token_type
        logger.debug("parse_statement: next statement token_type=%s", ttype.name)

        # 2) Dispatch based on the token type
        if ttype == LmnTokenType.FUNCTION:
            # Already have 'function' here, so consume it
            self.parser.advance()
            return FunctionDefinitionParser(self.parser).parse()
        
        elif ttype == LmnTokenType.IDENTIFIER:
            # e.g. myVar = 123
            return AssignmentParser(self.parser).parse()
        
        elif ttype == LmnTokenType.IF:
            return IfParser(self.parser).parse()

        elif ttype == LmnTokenType.FOR:
            return ForParser(self.parser).parse()

        elif ttype == LmnTokenType.LET:
            return LetParser(self.parser).parse()

        elif ttype == LmnTokenType.PRINT:
            return PrintParser(self.parser).parse()

        elif ttype == LmnTokenType.RETURN:
            return ReturnParser(self.parser).parse()
        
        elif ttype == LmnTokenType.BEGIN:
            return BlockParser(self.parser).parse()

        # 3) Possibly handle other statements (call, break, etc.) here.

        # 4) If none of the recognized statement tokens matched, it's unexpected:
        logger.debug(
            "parse_statement: found unrecognized token for statement => %s",
            ttype.name
        )
        raise SyntaxError(f"Unexpected token for statement: {ttype}")

# file: lmn/compiler/parser/statements/if_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.statements.if_statement import IfStatement
from lmn.compiler.ast.statements.else_if_clause import ElseIfClause
from lmn.compiler.parser.parser_utils import parse_block

logger = logging.getLogger(__name__)

class IfParser:
    def __init__(self, parent_parser):
        """
        parent_parser: The main Parser instance, which holds the token stream
                       and provides 'advance()', etc.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses an if/elseif/else block with optional parentheses around conditions.

        Grammar conceptually:
          IF condition_block
          { ELSEIF condition_block }
          [ ELSE block ]
          END

        Where condition_block = expression + block
        The expression parser itself handles any parentheses or operators.
        """

        logger.debug("Starting parse of 'if' statement. Current token: %s",
                     self.parser.current_token)

        # 1) If current token is IF, consume it
        if (self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.IF):
            logger.debug("Consuming 'if' token: %s", self.parser.current_token)
            self.parser.advance()

        # 2) Parse the 'if' condition
        if_condition = self._parse_if_condition()
        logger.debug("Parsed IF condition: %s", if_condition)

        # 3) Parse the 'then' block until ELSEIF, ELSE, or END
        if_block = parse_block(
            self.parser,
            until_tokens=[LmnTokenType.ELSEIF, LmnTokenType.ELSE, LmnTokenType.END]
        )

        # 4) Handle multiple 'elseif' sections
        elseif_clauses = []
        while (self.parser.current_token
               and self.parser.current_token.token_type == LmnTokenType.ELSEIF):
            logger.debug("Consuming 'elseif' token: %s", self.parser.current_token)
            self.parser.advance()  # skip 'elseif'
            logger.debug("Parsing ELSEIF. Current token: %s", self.parser.current_token)

            elif_condition = self._parse_if_condition()
            logger.debug("Parsed ELSEIF condition: %s", elif_condition)

            elif_block = parse_block(
                self.parser,
                until_tokens=[LmnTokenType.ELSEIF, LmnTokenType.ELSE, LmnTokenType.END]
            )

            clause = ElseIfClause(condition=elif_condition, body=elif_block)
            elseif_clauses.append(clause)
            logger.debug("Built ElseIfClause: %s", clause)

        # 5) Optional 'else'
        else_block = []
        if (self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.ELSE):
            logger.debug("Consuming 'else' token: %s", self.parser.current_token)
            self.parser.advance()
            logger.debug("Found ELSE. Current token: %s", self.parser.current_token)

            else_block = parse_block(
                self.parser,
                until_tokens=[LmnTokenType.END]
            )
            logger.debug("Parsed ELSE block with %d statements.",
                         len(else_block) if else_block else 0)

        # 6) Expect 'end'
        if (not self.parser.current_token
            or self.parser.current_token.token_type != LmnTokenType.END):
            raise SyntaxError("Expected 'end' to close if statement")

        logger.debug("Consuming 'end' for if statement: %s", self.parser.current_token)
        self.parser.advance()  # consume 'end'

        # 7) Build and return the IfStatement node
        return IfStatement(
            condition=if_condition,
            then_body=if_block,
            elseif_clauses=elseif_clauses,
            else_body=else_block
        )

    def _parse_if_condition(self):
        """
        Let the expression parser handle all parentheses and operators.
        e.g.
            if x < 10
            if (x + 5) < 10
            if ((x + 5) * y) < (z + 1)
        """
        self._skip_ignorable_tokens()

        token = self.parser.current_token
        if not token:
            raise SyntaxError("Unexpected end of tokens while parsing if-condition")

        logger.debug("Parsing if-condition. Current token: %s", token)

        # *** KEY CHANGE ***
        # Instead of special handling for '(' => parse partial expression and force ')',
        # we simply parse the entire expression (the expression parser can handle
        # parentheses in the middle of an expression).
        condition = self.parser.expression_parser.parse_expression()
        logger.debug("Parsed condition: %s", condition)

        if not condition:
            raise SyntaxError("Expected condition expression after 'if' or 'elseif'")

        return condition

    def _skip_ignorable_tokens(self):
        """
        Skip NEWLINE and COMMENT tokens so we see the real condition token
        right after 'if' or 'elseif'.
        """
        while (self.parser.current_token and
               self.parser.current_token.token_type in (
                   LmnTokenType.NEWLINE,
                   LmnTokenType.COMMENT
               )):
            logger.debug("Skipping ignorable token: %s", self.parser.current_token)
            self.parser.advance()

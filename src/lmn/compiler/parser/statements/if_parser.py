import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast.statements.if_statement import IfStatement
from lmn.compiler.ast.statements.else_if_clause import ElseIfClause
from lmn.compiler.parser.parser_utils import parse_block

logger = logging.getLogger(__name__)

class IfParser:
    def __init__(self, parent_parser):
        """
        Initializes the IfParser with a reference to the main parser.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses an if/elseif/else block with the following structure:
        
        if <condition>
          <statements>
        elseif <condition>
          <statements>
        else
          <statements>
        end
        """
        logger.debug(
            "IfParser: Starting to parse 'if' statement. Current token: %s",
            self.parser.current_token
        )

        # 1) Consume the 'if' token
        if self.parser.current_token and self.parser.current_token.token_type == LmnTokenType.IF:
            logger.debug("IfParser: Consuming 'if' token: %s", self.parser.current_token)
            self.parser.advance()

        # 2) Parse the 'if' condition
        if_condition = self._parse_if_condition()
        logger.debug("IfParser: Parsed IF condition: %s", if_condition)

        # 3) Parse the 'then' block
        if_block = parse_block(
            self.parser,
            until_tokens=[LmnTokenType.ELSEIF, LmnTokenType.ELSE, LmnTokenType.END]
        )
        logger.debug(
            "IfParser: Parsed IF block with %d statements.",
            len(if_block) if if_block else 0
        )

        # 4) Parse any 'elseif' clauses
        elseif_clauses = []
        while (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.ELSEIF
        ):
            logger.debug("IfParser: Found 'elseif' token: %s", self.parser.current_token)
            self.parser.advance()  # Consume 'elseif'

            elif_condition = self._parse_if_condition()
            logger.debug("IfParser: Parsed ELSEIF condition: %s", elif_condition)

            elif_block = parse_block(
                self.parser,
                until_tokens=[LmnTokenType.ELSEIF, LmnTokenType.ELSE, LmnTokenType.END]
            )
            logger.debug(
                "IfParser: Parsed ELSEIF block with %d statements.",
                len(elif_block) if elif_block else 0
            )

            clause = ElseIfClause(condition=elif_condition, body=elif_block)
            elseif_clauses.append(clause)
            logger.debug("IfParser: Built ElseIfClause: %s", clause)

        # 5) Parse the optional 'else' block
        else_block = []
        if (
            self.parser.current_token
            and self.parser.current_token.token_type == LmnTokenType.ELSE
        ):
            logger.debug("IfParser: Found 'else' token: %s", self.parser.current_token)
            self.parser.advance()  # Consume 'else'

            else_block = parse_block(
                self.parser,
                until_tokens=[LmnTokenType.END]
            )
            logger.debug(
                "IfParser: Parsed ELSE block with %d statements.",
                len(else_block) if else_block else 0
            )

        # 6) Ensure the 'if' statement ends with 'end'
        if (
            not self.parser.current_token
            or self.parser.current_token.token_type != LmnTokenType.END
        ):
            logger.error("IfParser: Missing 'end' to close 'if' statement.")
            raise SyntaxError("Expected 'end' to close if statement")

        logger.debug(
            "IfParser: Consuming 'end' token for 'if' statement: %s",
            self.parser.current_token
        )
        self.parser.advance()  # Consume 'end'

        # 7) Construct and return the IfStatement node
        if_statement = IfStatement(
            condition=if_condition,
            then_body=if_block,
            elseif_clauses=elseif_clauses,
            else_body=else_block
        )
        logger.debug("IfParser: Constructed IfStatement: %s", if_statement)

        return if_statement

    def _parse_if_condition(self):
        """
        Parses the condition of an 'if' or 'elseif' clause.
        """
        self._skip_ignorable_tokens()

        token = self.parser.current_token
        if not token:
            logger.error("IfParser: Unexpected end of tokens while parsing condition.")
            raise SyntaxError("Unexpected end of tokens while parsing if-condition")

        logger.debug("IfParser: Parsing condition. Current token: %s", token)

        # Delegate to the expression parser to handle the condition
        condition = self.parser.expression_parser.parse_expression()
        logger.debug("IfParser: Parsed condition: %s", condition)

        if not condition:
            logger.error("IfParser: Missing condition expression after 'if' or 'elseif'.")
            raise SyntaxError("Expected condition expression after 'if' or 'elseif'")

        return condition

    def _skip_ignorable_tokens(self):
        """
        Skips over ignorable tokens like NEWLINE and COMMENT.
        """
        while (
            self.parser.current_token
            and self.parser.current_token.token_type in (LmnTokenType.NEWLINE, LmnTokenType.COMMENT)
        ):
            logger.debug("IfParser: Skipping ignorable token: %s", self.parser.current_token)
            self.parser.advance()

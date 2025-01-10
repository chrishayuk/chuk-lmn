import logging
from lmn.compiler.ast.statements.block_statement import BlockStatement
from lmn.compiler.lexer.token_type import LmnTokenType

logger = logging.getLogger(__name__)

class BlockParser:
    def __init__(self, parent_parser):
        """
        Initializes the BlockParser with a reference to the main parser.
        """
        self.parser = parent_parser

    def parse(self):
        """
        Parses a block of statements between 'begin' and 'end', for example:

        begin
            let x: int
            x = 42
            print x
        end

        Note: Expects 'begin' token to already have been consumed by the statement parser.
        """
        logger.debug("BlockParser: Starting block parsing. Expecting 'end' to close block.")

        # 1) Consume 'begin' token (already confirmed by StatementParser).
        self.parser.advance()

        statements = []

        # 2) Keep parsing until we see 'end' or run out of tokens
        while self.parser.current_token is not None:
            token = self.parser.current_token
            logger.debug("BlockParser: Processing token %r", token)

            # a) Check for 'end'
            if token.token_type == LmnTokenType.END:
                logger.debug("BlockParser: Found 'end' token. Completing block parsing.")
                self.parser.advance()  # consume 'end'
                logger.debug("BlockParser: Completed block with %d statements.", len(statements))
                return BlockStatement(statements=statements)

            # b) Skip comments/newlines
            if token.token_type in (LmnTokenType.COMMENT, LmnTokenType.NEWLINE):
                logger.debug("BlockParser: Skipping token: %r", token)
                self.parser.advance()
                continue

            # c) Attempt to parse a statement (or possibly multiple statements)
            try:
                logger.debug("BlockParser: Attempting to parse a statement.")
                stmt_or_stmts = self.parser.statement_parser.parse_statement()

                if stmt_or_stmts:
                    # If parse_statement() returned multiple statements, flatten them
                    if isinstance(stmt_or_stmts, list):
                        statements.extend(stmt_or_stmts)
                        logger.debug(
                            "BlockParser: Received multiple statements, now total: %d",
                            len(statements)
                        )
                    else:
                        statements.append(stmt_or_stmts)
                        logger.debug("BlockParser: Parsed single statement: %r", stmt_or_stmts)
                else:
                    # If parse_statement() returns None, we likely encountered an unexpected token
                    logger.error("BlockParser: Unexpected token in block => %r", token)
                    raise SyntaxError(f"Unexpected token in block: {token.value} ({token.token_type})")

            except SyntaxError as e:
                logger.error("BlockParser: Syntax error encountered => %s", e)
                raise

        # 3) If we exit loop, no 'end' was found
        logger.error("BlockParser: Missing 'end' to close block.")
        raise SyntaxError("Expected 'end' to close block.")

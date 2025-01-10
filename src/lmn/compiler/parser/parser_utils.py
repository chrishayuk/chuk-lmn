# file: lmn/compiler/parser/parser_utils.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType

# logger
logger = logging.getLogger(__name__)

def expect_token(parser, token_types, message):
    """
    Confirms the parser's current token matches one of the expected types.
    Raises SyntaxError otherwise.

    :param parser: the parser with .current_token, .advance(), etc.
    :param token_types: a single LmnTokenType or an iterable of LmnTokenType items
    :param message: error message raised on failure
    :return: the current token on success
    """
    if not parser.current_token:
        logger.error("expect_token: No token found, expected one of: %r", token_types)
        raise SyntaxError(message)

    current_ttype = parser.current_token.token_type
    current_value = parser.current_token.value

    if not isinstance(token_types, (list, tuple, set)):
        token_types = (token_types,)

    logger.debug(
        "expect_token: Checking token '%s' (type=%s) against expected: %r",
        current_value,
        current_ttype.name,
        [t.name for t in token_types]
    )

    if current_ttype not in token_types:
        logger.error(
            "expect_token: Token mismatch. Got '%s' (type=%s), expected one of: %r",
            current_value,
            current_ttype.name,
            [t.name for t in token_types]
        )
        raise SyntaxError(message)

    logger.debug("expect_token: Matched token '%s' (type=%s)", current_value, current_ttype.name)
    return parser.current_token


def parse_block(parser, until_tokens):
    """
    Parses a block of statements until one of `until_tokens` is encountered.
    Skips comments. Returns a list of parsed statement nodes.

    If parse_statement() returns multiple statements (a list), we flatten them
    to avoid nested lists in the AST (e.g., [ [PrintStatement, BreakStatement] ]).
    """
    statements = []

    while parser.current_token and parser.current_token.token_type not in until_tokens:
        token = parser.current_token

        # Skip comments
        if token.token_type == LmnTokenType.COMMENT:
            logger.debug("parse_block: Skipping comment: %r", token.value)
            parser.advance()
            continue

        logger.debug("parse_block: Parsing statement. Current token: %r", token)

        try:
            stmt_or_stmts = parser.statement_parser.parse_statement()
            if stmt_or_stmts:
                # If parse_statement() returned multiple statements, flatten them
                if isinstance(stmt_or_stmts, list):
                    statements.extend(stmt_or_stmts)
                    logger.debug(
                        "parse_block: Received multiple statements, total now: %d",
                        len(statements)
                    )
                else:
                    statements.append(stmt_or_stmts)
                    logger.debug("parse_block: Parsed single statement: %r", stmt_or_stmts)
            else:
                # parse_statement returned None => likely unexpected token
                logger.warning("parse_block: parse_statement returned None for token: %r", token)
                break
        except SyntaxError as e:
            logger.error("parse_block: SyntaxError encountered: %s", e)
            raise

    logger.debug("parse_block: Completed block with %d statements", len(statements))
    return statements


def current_token_is(parser, token_type):
    """
    Checks if the current token matches the given token_type.

    :param parser: the main parser instance
    :param token_type: the token type to check against
    :return: True if current_token matches token_type, False otherwise
    """
    if parser.current_token is None:
        logger.debug("current_token_is: No current token to match against %s", token_type)
        return False

    if not isinstance(token_type, LmnTokenType):
        logger.error("current_token_is: Invalid token_type provided: %r", token_type)
        return False

    match = (parser.current_token.token_type == token_type)
    logger.debug(
        "current_token_is: Current token '%s' (type=%s) matches %s: %s",
        parser.current_token.value,
        parser.current_token.token_type.name,
        token_type.name,
        match
    )
    return match

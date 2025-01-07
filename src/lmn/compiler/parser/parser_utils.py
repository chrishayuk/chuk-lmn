# file: lmn/compiler/parser/parser_utils.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType

logger = logging.getLogger(__name__)

def expect_token(parser, token_types, message):
    """
    Utility to confirm parser.current_token has one of the expected types
    (or exactly the expected type if `token_types` is a single LmnTokenType).
    Raises SyntaxError otherwise.
    Returns the current token on success.

    :param parser: the parser with .current_token, .advance(), etc.
    :param token_types: either a single LmnTokenType or an iterable (tuple/list)
                       of LmnTokenType items
    :param message: an error message to raise if it fails
    """

    # 1) If we got no current token => can't match anything
    if not parser.current_token:
        logger.debug("expect_token: found NO token, but expected: %r", token_types)
        raise SyntaxError(message)

    current_ttype = parser.current_token.token_type
    current_value = parser.current_token.value

    # 2) Convert single token_type to a tuple for uniform check
    if not isinstance(token_types, (list, tuple, set)):
        token_types = (token_types,)

    # 3) Debug logging => show exactly what we see vs. what we expect
    logger.debug(
        "expect_token: current_token='%s'(type=%s), expecting one of %r",
        current_value, current_ttype.name, [t.name for t in token_types]
    )

    # 4) Check membership
    if current_ttype not in token_types:
        logger.debug(
            "expect_token: mismatch => got '%s'(type=%s), not in %r; raising SyntaxError",
            current_value, current_ttype.name, [t.name for t in token_types]
        )
        raise SyntaxError(message)

    logger.debug(
        "expect_token: matched token '%s'(type=%s) successfully.",
        current_value, current_ttype.name
    )
    return parser.current_token


def parse_block(parser, until_tokens):
    """
    Utility to parse a block of statements until we reach one of `until_tokens`.
    We skip comments along the way.
    Returns a list of statement AST nodes.
    """
    statements = []
    while parser.current_token and parser.current_token.token_type not in until_tokens:
        # skip comments
        if parser.current_token.token_type == LmnTokenType.COMMENT:
            logger.debug("parse_block: skipping comment: %r", parser.current_token.value)
            parser.advance()
            continue

        stmt = parser.statement_parser.parse_statement()
        if stmt:
            statements.append(stmt)
        else:
            # parse_statement returned None or we're stuck
            logger.debug(
                "parse_block: parse_statement() returned None; current_token=%s",
                parser.current_token
            )
            break
    return statements


def current_token_is(parser, token_type):
    """
    Returns True if parser.current_token is not None
    and matches the given token_type.
    """
    if parser.current_token is None:
        logger.debug("current_token_is: No current token, so can't match %s", token_type)
        return False

    match = (parser.current_token.token_type == token_type)
    logger.debug(
        "current_token_is: token=%r(type=%s), checking=%s => %s",
        parser.current_token.value,
        parser.current_token.token_type.name,
        token_type.name if isinstance(token_type, LmnTokenType) else token_type,
        match
    )
    return match

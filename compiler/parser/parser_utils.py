# compiler/parser/parser_utils.py
from compiler.lexer.token_type import LmnTokenType

def expect_token(parser, token_type, message):
    """
    Utility to confirm parser.current_token has the expected type.
    Raises SyntaxError otherwise.
    Returns the current token on success.
    """
    if not parser.current_token or parser.current_token.token_type != token_type:
        raise SyntaxError(message)
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
            parser.advance()
            continue
        stmt = parser.statement_parser.parse_statement()
        if stmt:
            statements.append(stmt)
        else:
            # parse_statement returned None or we're stuck
            break
    return statements

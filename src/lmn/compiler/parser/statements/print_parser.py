# file: lmn/compiler/parser/statements/print_parser.py

import logging
from lmn.compiler.lexer.token_type import LmnTokenType
from lmn.compiler.ast import PrintStatement
from lmn.compiler.parser.statements.statement_boundaries import is_statement_boundary

logger = logging.getLogger(__name__)

class PrintParser:
    def __init__(self, parent_parser):
        self.parser = parent_parser

    def parse(self):
        """
        Parses a 'print' statement, collecting zero or more expressions
        until hitting a statement boundary or a token that is not valid
        in an expression context (e.g., break).
        
        If 'break' is encountered, we route it to the statement parser
        to handle via 'BreakParser'.
        """
        logger.debug("PrintParser: Starting parse of 'print' statement.")
        
        # Consume the 'print' token
        self.parser.advance()

        expressions = []
        
        # Keep parsing expressions until we hit a statement boundary
        while (
            self.parser.current_token
            and not is_statement_boundary(self.parser.current_token.token_type)
        ):
            current_token = self.parser.current_token
            current_ttype = current_token.token_type

            logger.debug(
                "PrintParser: Attempting to parse next expression for 'print'. "
                "Current token: %r",
                current_token
            )

            # (A) If next token is `break` or `continue`, optionally dispatch to statement parser
            if current_ttype in (LmnTokenType.BREAK, LmnTokenType.CONTINUE):
                logger.debug(
                    "PrintParser: Token '%s' encountered in 'print' context. "
                    "Delegating to statement parser for handling.",
                    current_ttype.name
                )
                # Option 1: Call statement parser to handle `break` or `continue`
                stmt = self.parser.statement_parser.parse_statement()
                # If your language prohibits `print break;`, you might raise SyntaxError here instead:
                # raise SyntaxError(f"'{current_token.value}' is not valid as an expression in 'print'")
                
                # We'll break out of the expression loop if we handled it as a statement
                # so we only keep expressions parsed *before* break/continue in the PrintStatement
                break

            # (B) Otherwise, parse an expression via ExpressionParser
            expr = self.parser.expression_parser.parse_expression()
            if expr is None:
                logger.debug("PrintParser: No expression parsed or boundary reached.")
                break

            # Add the parsed expression
            expressions.append(expr)
            logger.debug("PrintParser: Parsed and added expression => %r", expr)

        logger.debug(
            "PrintParser: Building PrintStatement with %d expression(s).",
            len(expressions)
        )
        return PrintStatement(expressions=expressions)

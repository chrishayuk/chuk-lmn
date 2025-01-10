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
        until hitting a statement boundary or a 'break'/ 'continue' token.
        
        Returns a *list* of statements:
          - 1st element: PrintStatement with any expressions parsed
          - 2nd element (optional): BreakStatement or ContinueStatement if encountered
        """
        logger.debug("PrintParser: Starting parse of 'print' statement.")
        
        # 1) Consume the 'print' token
        self.parser.advance()  # consumes 'print'

        expressions = []
        secondary_stmt = None  # if we parse a break/continue, store it here
        
        # 2) Keep parsing expressions until statement boundary or break/continue
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

            if current_ttype in (LmnTokenType.BREAK, LmnTokenType.CONTINUE):
                logger.debug(
                    "PrintParser: Token '%s' encountered in 'print' context. "
                    "Delegating to statement parser for handling.",
                    current_ttype.name
                )
                # Let the statement parser parse the break/continue
                secondary_stmt = self.parser.statement_parser.parse_statement()
                
                # Stop parsing more expressions; we only keep what's parsed so far
                break

            else:
                # Parse an expression via ExpressionParser
                expr = self.parser.expression_parser.parse_expression()
                if expr is None:
                    logger.debug("PrintParser: No expression parsed or boundary reached.")
                    break

                expressions.append(expr)
                logger.debug("PrintParser: Parsed and added expression => %r", expr)

        logger.debug(
            "PrintParser: Building PrintStatement with %d expression(s).",
            len(expressions)
        )

        # 3) Always build the PrintStatement for the expressions we found
        print_stmt = PrintStatement(expressions=expressions)

        # 4) Return a *list* of statements
        #    - If we never saw a 'break'/'continue', this list has just the print_stmt
        #    - If we did parse a 'break'/'continue', we also append that statement
        if secondary_stmt:
            return [print_stmt, secondary_stmt]
        else:
            return [print_stmt]

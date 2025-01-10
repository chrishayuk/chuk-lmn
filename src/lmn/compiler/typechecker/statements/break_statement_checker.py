# file: lmn/compiler/typechecker/statements/break_statement_checker.py
import logging
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class BreakStatementChecker(BaseStatementChecker):
    """
    A checker for BreakStatement nodes.
    """

    def check(self, stmt, local_scope=None):
        """
        Type-check a BreakStatement. Typically:
          - Ensure we are in a loop context.
          - Inferred type is 'void'.
        """
        if local_scope is None:
            local_scope = self.symbol_table

        logger.debug("Checking a BreakStatement...")

        # Optional: check if we are inside a loop
        in_loop = local_scope.get("__in_loop__", False)
        if not in_loop:
            # If your language disallows break outside loops, raise an error:
            raise TypeError("Break statement used outside of a loop context.")

        # Mark it as void, since 'break' doesn't produce a value
        stmt.inferred_type = "void"

        logger.debug("Finished checking BreakStatement => type=void")
        return None

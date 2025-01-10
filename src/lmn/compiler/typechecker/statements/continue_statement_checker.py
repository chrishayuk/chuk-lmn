# file: lmn/compiler/typechecker/statements/continue_statement_checker.py
import logging
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class ContinueStatementChecker(BaseStatementChecker):
    """
    A checker for ContinueStatement nodes.
    """

    def check(self, stmt, local_scope=None):
        """
        Type-check a ContinueStatement. Typically:
          - Ensure we are in a loop context.
          - Inferred type is 'void'.
        """
        if local_scope is None:
            local_scope = self.symbol_table

        logger.debug("Checking a ContinueStatement...")

        # Optional: check if we are inside a loop
        in_loop = local_scope.get("__in_loop__", False)
        if not in_loop:
            # If your language disallows continue outside loops, raise an error:
            raise TypeError("Continue statement used outside of a loop context.")

        # Mark it as void
        stmt.inferred_type = "void"

        logger.debug("Finished checking ContinueStatement => type=void")
        return None

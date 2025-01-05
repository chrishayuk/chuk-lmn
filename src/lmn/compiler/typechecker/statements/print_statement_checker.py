# file: lmn/compiler/typechecker/statements/print_statement_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class PrintStatementChecker(BaseStatementChecker):
    """
    A checker for PrintStatement nodes.
    """

    def check(self, stmt, local_scope=None):
        """
        Type-check a PrintStatement by type-checking each expression
        to be printed, but otherwise we don't unify or store anything.

        If local_scope is provided, we use it for variable lookups.
        """
        # Decide which scope to use for expression checks
        scope = local_scope if local_scope is not None else self.symbol_table

        # Loop through each expression
        for expr in stmt.expressions:
            # Check the expression in the given scope
            e_type = self.dispatcher.check_expression(expr, local_scope=scope)
            logger.debug(f"Print expr '{expr}' resolved to type {e_type}")

        # Mark the statement as "void"
        stmt.inferred_type = "void"

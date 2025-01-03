# file: lmn/compiler/typechecker/statements/print_statement_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

# logger
logger = logging.getLogger(__name__)

class PrintStatementChecker(BaseStatementChecker):
    """
    A checker for PrintStatement nodes.
    """

    def check(self, stmt):
        """
        Type-check a PrintStatement by type-checking each expression
        to be printed, but otherwise we don't unify or store anything.
        """
        # loop through each expression
        for expr in stmt.expressions:
            # check the expression and get its inferred type
            e_type = self.dispatcher.check_expression(expr)
            logger.debug(f"Print expr '{expr}' resolved to type {e_type}")

        # Optionally mark the statement as "void"
        stmt.inferred_type = "void"

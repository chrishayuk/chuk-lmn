# file: lmn/compiler/typechecker/statements/block_statement_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

# logging
logger = logging.getLogger(__name__)

class BlockStatementChecker(BaseStatementChecker):
    """
    A checker for BlockStatement nodes.
    """

    def check(self, stmt):
        """
        Type-check a block by creating a local scope so new variables 
        won't leak out.
        """
        logger.debug("Entering new block scope")
        local_scope = dict(self.symbol_table)

        # Type-check each statement in the block
        for child_stmt in stmt.statements:
            # Check the statement in the current scope
            self.dispatcher.check_statement(child_stmt, local_scope)

        logger.debug("Exiting block scope. Local declarations are discarded.")
        logger.debug(f"Symbol table remains (outer scope) = {self.symbol_table}")

        # Mark block as "void"
        stmt.inferred_type = "void"

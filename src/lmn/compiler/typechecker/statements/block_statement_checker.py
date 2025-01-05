# file: lmn/compiler/typechecker/statements/block_statement_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class BlockStatementChecker(BaseStatementChecker):
    """
    A checker for BlockStatement nodes.
    """

    def check(self, stmt):
        """
        Type-check a block by creating a local scope so new variables 
        won't leak out. Reassignments inside the block also do not 
        affect the parent scope outside the block.
        """
        logger.debug("Entering new block scope")

        # 1) Make a shallow copy of the parent's symbol table
        local_scope = dict(self.symbol_table)

        # 2) Also copy the parent's assigned-vars set (if any),
        #    so the block can see which variables are already assigned
        parent_assigned_vars = self.symbol_table.get("__assigned_vars__", set())
        local_assigned_vars = set(parent_assigned_vars)  # make a copy

        # 3) Likewise copy any special keys such as __current_function_return_type__
        parent_return_type = self.symbol_table.get("__current_function_return_type__", None)
        if parent_return_type:
            local_scope["__current_function_return_type__"] = parent_return_type

        # 4) Now update local_scope with the local assigned-vars copy
        local_scope["__assigned_vars__"] = local_assigned_vars

        # 5) Type-check each statement in this block using local_scope
        for child_stmt in stmt.statements:
            self.dispatcher.check_statement(child_stmt, local_scope)

        logger.debug("Exiting block scope. Local declarations/assignments do NOT leak out.")
        logger.debug(f"Symbol table remains (outer scope) = {self.symbol_table}")

        # 6) Mark block as "void"
        stmt.inferred_type = "void"

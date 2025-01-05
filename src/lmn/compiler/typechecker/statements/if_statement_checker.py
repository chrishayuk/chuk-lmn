# file: lmn/compiler/typechecker/statements/if_statement_checker.py
import logging

# lmn
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class IfStatementChecker(BaseStatementChecker):
    """
    A checker for IfStatement nodes.
    """

    def check(self, stmt, local_scope=None):
        """
        1) Type-check the condition
        2) Type-check 'then' block
        3) For each 'elseif' clause, type-check the condition and block
        4) Type-check 'else' block if present
        5) Mark the IfStatement as "void"
        """

        # Decide which scope to use for lookups
        scope = local_scope if local_scope is not None else self.symbol_table

        # 1) Condition
        cond_type = self.dispatcher.check_expression(stmt.condition, local_scope=scope)
        logger.debug(f"If condition type: {cond_type}")

        # check that the condition is 'int' or 'bool'
        if cond_type not in ("int", "bool"):
            raise TypeError(f"If condition must be int/bool, got '{cond_type}'")

        # 2) Then body => new local scope
        then_scope = dict(scope)
        for child_stmt in stmt.then_body:
            self.dispatcher.check_statement(child_stmt, then_scope)

        # 3) ElseIf clauses => each has its own local scope from the parent
        if hasattr(stmt, "elseif_clauses"):
            for elseif_clause in stmt.elseif_clauses:
                elseif_cond_type = self.dispatcher.check_expression(
                    elseif_clause.condition,
                    local_scope=scope
                )
                if elseif_cond_type not in ("int", "bool"):
                    raise TypeError(
                        f"ElseIf condition must be int/bool, got '{elseif_cond_type}'"
                    )

                elseif_scope = dict(scope)
                for child_stmt in elseif_clause.body:
                    self.dispatcher.check_statement(child_stmt, elseif_scope)

        # 4) Else body => another local scope from the parent
        if stmt.else_body:
            else_scope = dict(scope)
            for child_stmt in stmt.else_body:
                self.dispatcher.check_statement(child_stmt, else_scope)

        # 5) Mark the entire IfStatement as "void"
        stmt.inferred_type = "void"
        logger.debug("IfStatementChecker: finished checking if-statement")

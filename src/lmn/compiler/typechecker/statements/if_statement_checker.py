# file: lmn/compiler/typechecker/statements/if_statement_checker.py
import logging

# lmn
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

# logger
logger = logging.getLogger(__name__)

class IfStatementChecker(BaseStatementChecker):
    """
    A checker for IfStatement nodes.
    """

    def check(self, stmt):
        """
        1) Type-check the condition
        2) Type-check 'then' block
        3) For each 'elseif' clause, type-check the condition and block
        4) Type-check 'else' block if present
        5) Mark the IfStatement as "void"
        """
        # 1) Condition
        # check the condition
        cond_type = self.dispatcher.check_expression(stmt.condition)
        logger.debug(f"If condition type: {cond_type}")

        # check that the condition is a boolean
        if cond_type not in ("int", "bool"):
            raise TypeError(f"If condition must be int/bool, got '{cond_type}'")

        # 2) Then body
        for child_stmt in stmt.then_body:
            # check the statement
            self.dispatcher.check_statement(child_stmt)

        # 3) ElseIf clauses
        if hasattr(stmt, "elseif_clauses"):
            # check each ElseIf clause
            for elseif_clause in stmt.elseif_clauses:
                # check the condition
                elseif_cond_type = self.dispatcher.check_expression(elseif_clause.condition)

                # check that the condition is a boolean
                if elseif_cond_type not in ("int", "bool"):
                    # raise an error
                    raise TypeError(f"ElseIf condition must be int/bool, got '{elseif_cond_type}'")
                
                # check each statement of the body
                for child_stmt in elseif_clause.body:
                    # check each statement
                    self.dispatcher.check_statement(child_stmt)

        # 4) Else body
        if stmt.else_body:
            # check each statement of the else body
            for child_stmt in stmt.else_body:
                # check each statement
                self.dispatcher.check_statement(child_stmt)

        # 5) Mark the entire IfStatement as "void"
        stmt.inferred_type = "void"
        logger.debug("typechecker: finished check_if_statement")

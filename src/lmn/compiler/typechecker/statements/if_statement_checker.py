import logging

# lmn
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

class IfStatementChecker(BaseStatementChecker):
    """
    A checker for IfStatement nodes that treats 'if' as an expression
    producing a unified type from all branches, *and* also merges any
    changes to '__current_function_return_type__' back into the parent scope.
    """

    def check(self, stmt, local_scope=None):
        """
        1) Type-check the condition => must be 'int' or 'bool'
        2) Type-check 'then' block => gather last statement's type
           & unify function return type w/ parent's.
        3) For each 'elseif' => same as step #2
        4) Type-check 'else' block => gather last statement's type
           & unify function return type w/ parent's.
        5) Unify all branch types => stmt.inferred_type
        """

        scope = local_scope if local_scope is not None else self.symbol_table

        # 1) Condition
        cond_type = self.dispatcher.check_expression(stmt.condition, local_scope=scope)
        logger.debug(f"[IfStatementChecker] Condition type => {cond_type}")

        if cond_type not in ("int", "bool"):
            raise TypeError(f"If condition must be int/bool, got '{cond_type}'")

        # We'll track a list of branch result types to unify
        branch_types = []

        # ------------------------------------------------------------
        # 2) Then body => child scope
        # ------------------------------------------------------------
        logger.debug("[IfStatementChecker] Entering 'then' block scope...")
        then_scope = dict(scope)
        for child_stmt in stmt.then_body:
            self.dispatcher.check_statement(child_stmt, then_scope)

        if stmt.then_body:
            last_stmt = stmt.then_body[-1]
            then_block_type = getattr(last_stmt, "inferred_type", "void")
        else:
            then_block_type = "void"

        # Unify parent's function return type if the child updated it
        self._merge_child_return_type_into_parent(then_scope, scope, block_name="then")

        branch_types.append(then_block_type)
        logger.debug(
            f"[IfStatementChecker] Then block final type => {then_block_type}"
        )

        # ------------------------------------------------------------
        # 3) ElseIf clauses
        # ------------------------------------------------------------
        if hasattr(stmt, "elseif_clauses"):
            for (i, elseif_clause) in enumerate(stmt.elseif_clauses, start=1):
                logger.debug(f"[IfStatementChecker] Entering 'elseif' #{i} block scope...")
                elseif_cond_type = self.dispatcher.check_expression(
                    elseif_clause.condition,
                    local_scope=scope
                )
                logger.debug(f"[IfStatementChecker] ElseIf condition => {elseif_cond_type}")

                if elseif_cond_type not in ("int", "bool"):
                    raise TypeError(
                        f"ElseIf condition must be int/bool, got '{elseif_cond_type}'"
                    )

                elseif_scope = dict(scope)
                for child_stmt in elseif_clause.body:
                    self.dispatcher.check_statement(child_stmt, elseif_scope)

                if elseif_clause.body:
                    last_elseif_stmt = elseif_clause.body[-1]
                    elseif_block_type = getattr(last_elseif_stmt, "inferred_type", "void")
                else:
                    elseif_block_type = "void"

                # Merge function return type from child scope
                self._merge_child_return_type_into_parent(elseif_scope, scope, block_name=f"elseif#{i}")

                branch_types.append(elseif_block_type)
                logger.debug(
                    f"[IfStatementChecker] ElseIf #{i} block final type => {elseif_block_type}"
                )

        # ------------------------------------------------------------
        # 4) Else body => child scope
        # ------------------------------------------------------------
        if stmt.else_body:
            logger.debug("[IfStatementChecker] Entering 'else' block scope...")
            else_scope = dict(scope)
            for child_stmt in stmt.else_body:
                self.dispatcher.check_statement(child_stmt, else_scope)

            if stmt.else_body:
                last_else_stmt = stmt.else_body[-1]
                else_block_type = getattr(last_else_stmt, "inferred_type", "void")
            else:
                else_block_type = "void"

            # Merge function return type from child scope
            self._merge_child_return_type_into_parent(else_scope, scope, block_name="else")

            branch_types.append(else_block_type)
            logger.debug(
                f"[IfStatementChecker] Else block final type => {else_block_type}"
            )

        # ------------------------------------------------------------
        # 5) Unify all branch types => the if-stmt's type
        # ------------------------------------------------------------
        final_type = branch_types[0]
        for t in branch_types[1:]:
            final_type = unify_types(final_type, t, for_assignment=False)

        stmt.inferred_type = final_type
        logger.debug(
            f"[IfStatementChecker] Finished checking if-statement => {final_type}"
        )

    def _merge_child_return_type_into_parent(self, child_scope, parent_scope, block_name=""):
        """
        If the child scope's __current_function_return_type__ is not None,
        unify it with the parent's so we don't lose an 'int' update
        if the parent was 'void' or None.
        """
        child_ret = child_scope.get("__current_function_return_type__")
        parent_ret = parent_scope.get("__current_function_return_type__")

        logger.debug(
            f"[IfStatementChecker] Merging {block_name} scope return_type => "
            f"child_ret={child_ret}, parent_ret={parent_ret}"
        )

        if child_ret is not None:
            # unify them
            new_ret = unify_types(parent_ret, child_ret, for_assignment=False)
            parent_scope["__current_function_return_type__"] = new_ret

            logger.debug(
                f"[IfStatementChecker] After merging {block_name} scope => "
                f"parent_ret={parent_scope['__current_function_return_type__']}"
            )


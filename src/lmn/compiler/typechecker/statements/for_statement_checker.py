# file: lmn/compiler/typechecker/statements/for_statement_checker.py

import logging

from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class ForStatementChecker(BaseStatementChecker):
    def check(self, stmt, local_scope=None):
        """
        Type-check a ForStatement node, which likely has:
        
        stmt.variable    => a VariableExpression object
        stmt.start_expr  => Expression (range-based) or array ref (for-in loop)
        stmt.end_expr    => Expression (for range-based) or None for for-in
        stmt.body        => list of statement nodes inside the loop
        """
        logger.debug("Checking a ForStatement...")

        # 1) Decide which scope to use
        if local_scope is None:
            local_scope = self.symbol_table
        
        # Debug: Print parent's scope info
        parent_assigned_vars = local_scope.get("__assigned_vars__", set())
        logger.debug(
            f"[ForStatement] Parent local_scope keys = {list(local_scope.keys())}"
        )
        logger.debug(
            f"[ForStatement] Parent assigned_vars = {parent_assigned_vars}"
        )

        # 2) Range-based vs. for-in
        if self._is_range_based(stmt):
            self._check_range_based_for(stmt, local_scope)
        else:
            self._check_for_in_loop(stmt, local_scope)

        # 3) Mark the ForStatement itself as "void"
        stmt.inferred_type = "void"
        logger.debug("Finished checking ForStatement.")

    def _is_range_based(self, stmt):
        """
        If stmt.end_expr is not None, we treat it as a range-based for:
          for i = start_expr to end_expr
        Otherwise, it’s "for item in arr".
        """
        return stmt.end_expr is not None

    def _check_range_based_for(self, stmt, local_scope):
        var_name   = stmt.variable.name
        start_expr = stmt.start_expr
        end_expr   = stmt.end_expr
        body_stmts = stmt.body

        logger.debug(f"Range-based for => variable: {var_name}")
        logger.debug(f"Range-based for => start_expr={start_expr}, end_expr={end_expr}")

        # a) Type-check start_expr and end_expr
        logger.debug(f"[Range-based] Checking start_expr with local_scope keys = {list(local_scope.keys())}")
        # Fix #1: pass local_scope as a keyword argument
        start_type = self.dispatcher.check_expression(start_expr, local_scope=local_scope)

        logger.debug(f"[Range-based] Checking end_expr with local_scope keys = {list(local_scope.keys())}")
        # Fix #2: pass local_scope as a keyword argument
        end_type   = self.dispatcher.check_expression(end_expr, local_scope=local_scope)

        logger.debug(f"start_type={start_type}, end_type={end_type}")

        # b) Create a loop-local scope
        loop_scope = dict(local_scope)
        assigned_vars = set(loop_scope.get("__assigned_vars__", set()))
        loop_scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            "[Range-based] Creating loop_scope for range-based for.\n"
            f"Parent assigned_vars = {local_scope.get('__assigned_vars__', set())}\n"
            f"loop_scope keys pre-assign = {list(loop_scope.keys())}\n"
            f"Currently assigned vars (copy) = {assigned_vars}"
        )

        # c) Mark loop variable as assigned and set its type
        loop_scope[var_name] = "int"
        assigned_vars.add(var_name)
        
        logger.debug(
            f"[Range-based] Marked loop variable '{var_name}' as assigned with type 'int'.\n"
            f"assigned_vars now = {assigned_vars}\n"
            f"loop_scope keys now = {list(loop_scope.keys())}"
        )

        # d) Type-check the loop body
        for child_stmt in body_stmts:
            logger.debug(
                f"[Range-based] Type-checking statement in loop body: {child_stmt.type}\n"
                f"loop_scope keys = {list(loop_scope.keys())}, assigned_vars = {assigned_vars}"
            )
            self.dispatcher.check_statement(child_stmt, loop_scope)
            logger.debug(
                f"[Range-based] After statement '{child_stmt.type}', assigned_vars = "
                f"{loop_scope.get('__assigned_vars__', set())}\n"
                f"loop_scope keys = {list(loop_scope.keys())}"
            )

        # e) (Optional) Remove the loop variable if your language requires block scoping
        # del loop_scope[var_name]
        # assigned_vars.discard(var_name)

    def _check_for_in_loop(self, stmt, local_scope):
        var_name   = stmt.variable.name
        arr_expr   = stmt.start_expr
        body_stmts = stmt.body

        logger.debug(f"For-in loop => variable: {var_name}")
        logger.debug(f"For-in loop => arr_expr={arr_expr}")

        # a) Type-check the array/collection expression
        logger.debug(f"[For-in] Checking arr_expr with local_scope keys = {list(local_scope.keys())}")
        # Fix: pass local_scope explicitly as a keyword
        arr_type = self.dispatcher.check_expression(arr_expr, local_scope=local_scope)
        logger.debug(f"arr_type={arr_type}")

        # b) Create a loop-local scope
        loop_scope = dict(local_scope)
        assigned_vars = set(loop_scope.get("__assigned_vars__", set()))
        loop_scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            "[For-in] Creating loop_scope for for-in loop.\n"
            f"Parent assigned_vars = {local_scope.get('__assigned_vars__', set())}\n"
            f"loop_scope keys pre-assign = {list(loop_scope.keys())}\n"
            f"Currently assigned vars (copy) = {assigned_vars}"
        )

        # c) Assume the element type is 'any' or unify from arr_type
        element_type = "any"
        # Example logic:
        #   if arr_type and arr_type.endswith("[]"):
        #       element_type = arr_type[:-2]

        loop_scope[var_name] = element_type
        assigned_vars.add(var_name)
        
        logger.debug(
            f"[For-in] Marked loop variable '{var_name}' as assigned with type '{element_type}'.\n"
            f"assigned_vars now = {assigned_vars}\n"
            f"loop_scope keys now = {list(loop_scope.keys())}"
        )

        # d) Type-check the loop body
        for child_stmt in body_stmts:
            logger.debug(
                f"[For-in] Type-checking statement in loop body: {child_stmt.type}\n"
                f"loop_scope keys = {list(loop_scope.keys())}, assigned_vars = {assigned_vars}"
            )
            self.dispatcher.check_statement(child_stmt, loop_scope)
            logger.debug(
                f"[For-in] After statement '{child_stmt.type}', assigned_vars = "
                f"{loop_scope.get('__assigned_vars__', set())}\n"
                f"loop_scope keys = {list(loop_scope.keys())}"
            )

        # e) (Optional) remove from scope if language scoping demands
        # del loop_scope[var_name]
        # assigned_vars.discard(var_name)

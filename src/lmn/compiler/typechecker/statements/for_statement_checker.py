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

        if local_scope is None:
            local_scope = self.symbol_table
        
        parent_assigned_vars = local_scope.get("__assigned_vars__", set())
        logger.debug(f"[ForStatement] Parent local_scope keys = {list(local_scope.keys())}")
        logger.debug(f"[ForStatement] Parent assigned_vars = {parent_assigned_vars}")

        # Decide if it’s range-based or for-in
        if self._is_range_based(stmt):
            self._check_range_based_for(stmt, local_scope)
        else:
            self._check_for_in_loop(stmt, local_scope)

        # Mark the ForStatement itself as "void" (no return type)
        stmt.inferred_type = "void"
        logger.debug("Finished checking ForStatement.")

    def _is_range_based(self, stmt):
        """
        If stmt.end_expr is not None, treat it as range-based for:
            for i = start_expr to end_expr
        Otherwise, "for item in arr".
        """
        return stmt.end_expr is not None

    def _check_range_based_for(self, stmt, local_scope):
        var_name   = stmt.variable.name
        start_expr = stmt.start_expr
        end_expr   = stmt.end_expr
        body_stmts = stmt.body

        logger.debug(f"Range-based for => variable: {var_name}")
        logger.debug(f"Range-based for => start_expr={start_expr}, end_expr={end_expr}")

        # (A) Check start_expr and end_expr
        logger.debug(f"[Range-based] Checking start_expr with local_scope keys = {list(local_scope.keys())}")
        start_type = self.dispatcher.check_expression(start_expr, local_scope=local_scope)

        logger.debug(f"[Range-based] Checking end_expr with local_scope keys = {list(local_scope.keys())}")
        end_type   = self.dispatcher.check_expression(end_expr, local_scope=local_scope)

        logger.debug(f"start_type={start_type}, end_type={end_type}")

        # (B) Create a loop-local scope so loop var & assigned vars don’t leak
        loop_scope = dict(local_scope)
        assigned_vars = set(loop_scope.get("__assigned_vars__", set()))
        loop_scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            "[Range-based] Creating loop_scope for range-based for.\n"
            f"Parent assigned_vars = {local_scope.get('__assigned_vars__', set())}\n"
            f"loop_scope keys pre-assign = {list(loop_scope.keys())}\n"
            f"Currently assigned vars (copy) = {assigned_vars}"
        )

        # *** Mark that we’re in a loop context ***
        loop_scope["__in_loop__"] = True

        # (C) Mark the loop variable as assigned and set its type
        loop_scope[var_name] = "int"
        assigned_vars.add(var_name)
        
        logger.debug(
            f"[Range-based] Marked loop variable '{var_name}' as assigned with type 'int'.\n"
            f"assigned_vars now = {assigned_vars}\n"
            f"loop_scope keys now = {list(loop_scope.keys())}"
        )

        # (D) Type-check each statement in the loop body
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

        # (E) (Optional) if your language demands removing loop var after block
        # del loop_scope[var_name]
        # assigned_vars.discard(var_name)

    def _check_for_in_loop(self, stmt, local_scope):
        var_name   = stmt.variable.name
        arr_expr   = stmt.start_expr
        body_stmts = stmt.body

        logger.debug(f"For-in loop => variable: {var_name}")
        logger.debug(f"For-in loop => arr_expr={arr_expr}")

        # (A) Type-check the array/collection expression
        logger.debug(f"[For-in] Checking arr_expr with local_scope keys = {list(local_scope.keys())}")
        arr_type = self.dispatcher.check_expression(arr_expr, local_scope=local_scope)
        logger.debug(f"arr_type={arr_type}")

        # (B) Create a loop-local scope
        loop_scope = dict(local_scope)
        assigned_vars = set(loop_scope.get("__assigned_vars__", set()))
        loop_scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            "[For-in] Creating loop_scope for for-in loop.\n"
            f"Parent assigned_vars = {local_scope.get('__assigned_vars__', set())}\n"
            f"loop_scope keys pre-assign = {list(loop_scope.keys())}\n"
            f"Currently assigned vars (copy) = {assigned_vars}"
        )

        # *** Mark that we’re in a loop context ***
        loop_scope["__in_loop__"] = True

        # (C) Decide the element_type
        element_type = "any"
        # If arr_type == "int[]" => element_type = "int"
        # (You can do your unify logic here.)

        loop_scope[var_name] = element_type
        assigned_vars.add(var_name)
        
        logger.debug(
            f"[For-in] Marked loop variable '{var_name}' as assigned with type '{element_type}'.\n"
            f"assigned_vars now = {assigned_vars}\n"
            f"loop_scope keys now = {list(loop_scope.keys())}"
        )

        # (D) Type-check the loop body
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

        # (E) (Optional) if your language demands removing loop var after block
        # del loop_scope[var_name]
        # assigned_vars.discard(var_name)

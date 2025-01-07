# file: lmn/compiler/typechecker/expressions/anonymous_function_checker.py

from typing import Optional, Dict, Any, List
import logging

from lmn.compiler.typechecker.expressions.base_expression_checker import BaseExpressionChecker
from lmn.compiler.typechecker.utils import unify_types

logger = logging.getLogger(__name__)

class AnonymousFunctionChecker(BaseExpressionChecker):
    def check(
        self,
        expr: "AnonymousFunctionExpression",
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        logger.debug("AnonymousFunctionChecker: Checking an anonymous function node...")

        parameters = expr.parameters       # e.g. [("y", "int")]
        declared_ret_type = expr.return_type  # e.g. "int" (could be None/void)
        body_stmts = expr.body

        # 1) Create child scope for parameters
        child_scope = dict(local_scope or {})
        for (p_name, p_type) in parameters:
            if not p_type:
                p_type = "int"
            child_scope[p_name] = p_type

        # 2) Track the function's final return type.
        #    - If user declared a return type, we start with that.
        #    - Otherwise, we infer from the body statements (possibly defaulting to "void").
        final_return_type = declared_ret_type or "void"

        # 3) We'll pass that child function return type to the statement dispatcher
        from lmn.compiler.typechecker.statements.statement_dispatcher import StatementDispatcher
        stmt_dispatcher = StatementDispatcher(
            self.symbol_table,  # global symbol table
            self.dispatcher
        )

        # 4) Actually walk child function body statements,
        #    unifying each ReturnStatement's expression type with final_return_type.
        for stmt in body_stmts:
            stmt_type = stmt_dispatcher.check_statement(
                stmt,
                child_scope,
                function_return_type=final_return_type
            )
            # If 'stmt' is a ReturnStatement with an expression => 
            # the ReturnStatementChecker likely unifies with final_return_type
            # or updates the scope's __current_function_return_type__.

        # (Optionally, you can gather the real final_return_type from child_scope
        # if ReturnStatements updated it. For example:
        possible_ret = child_scope.get("__current_function_return_type__")
        if possible_ret:
            # unify it with final_return_type
            final_return_type = unify_types(final_return_type, possible_ret, for_assignment=False)

        # 5) Instead of returning just "function", we produce a **closure dictionary**.
        #    That way, any subsequent calls see param_names, param_types, and return_type.
        closure_info = {
            "is_closure": True,
            # param_names => e.g. ["y"]
            "param_names": [p[0] for p in parameters],
            # param_types => e.g. ["int"], using the fallback or the declared param type
            "param_types": [p[1] if p[1] else "int" for p in parameters],
            # final_return_type => e.g. "int" or "void"
            "return_type": final_return_type
        }

        # Store this dictionary on the expression node
        expr.inferred_type = closure_info

        logger.debug(
            "AnonymousFunctionChecker done. declared_ret_type=%s => returning a closure %r",
            declared_ret_type,
            closure_info
        )

        # Return the dictionary so the caller (e.g. LetStatementChecker) can store it
        # in the symbol table if needed (e.g. let myFunc = (x) => x+1).
        return closure_info

# file: lmn/compiler/typechecker/statements/call_statement_checker.py
import logging
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker

logger = logging.getLogger(__name__)

class CallStatementChecker(BaseStatementChecker):
    """
    A checker for 'CallStatement' nodes.
    This typically involves calling a function or tool_name,
    e.g. `myFunction(arg1, arg2)` as a statement (no return).
    """

    def check(self, stmt, local_scope=None):
        """
        Type-check a CallStatement, which has something like:
            stmt.tool_name (the function or tool being called)
            stmt.arguments (the expression nodes for call arguments)

        :param stmt: the CallStatement AST node
        :param local_scope: a dictionary for local lookups if available
        """
        logger.debug("Checking a CallStatement...")

        # 1) Decide which scope to use
        if local_scope is None:
            local_scope = self.symbol_table

        # 2) Debug logs
        logger.debug(f"[CallStatementChecker] tool_name = {stmt.tool_name}")
        logger.debug(f"[CallStatementChecker] arguments = {stmt.arguments}")
        logger.debug(f"[CallStatementChecker] local_scope keys = {list(local_scope.keys())}")

        # 3) We typically want to:
        #    - Ensure the 'tool_name' is known in the symbol table (or globally).
        #    - Type-check each argument expression.

        # a) Check if 'tool_name' is recognized
        tool_info = local_scope.get(stmt.tool_name, None)
        if tool_info is None:
            # Possibly the tool_name is in the global table if not local
            tool_info = self.symbol_table.get(stmt.tool_name, None)
            if tool_info is None:
                raise NameError(f"Call to unknown function/tool '{stmt.tool_name}'")

        # b) Type-check each argument
        #    We'll call self.dispatcher.check_expression(...) for each argument
        #    so they are type-checked properly.
        arg_types = []
        for i, arg in enumerate(stmt.arguments):
            arg_type = self.dispatcher.check_expression(arg, local_scope=local_scope)
            arg_types.append(arg_type)
            logger.debug(f"[CallStatementChecker] Argument #{i} => type={arg_type}")

        # c) (Optional) unify param_types from tool_info with the actual arg_types
        #    If your language enforces strict param counts or types, do it here:
        #    param_names   = tool_info.get("param_names", [])
        #    param_types   = tool_info.get("param_types", [])
        #    unify or check each arg_type matches param_types[i]

        # d) This is a statement, not an expression, so no return type.
        #    You might set `stmt.inferred_type = "void"` or similar.
        stmt.inferred_type = "void"
        logger.debug("[CallStatementChecker] Finished checking CallStatement => type=void")

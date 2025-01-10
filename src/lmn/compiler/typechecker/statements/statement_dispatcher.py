# file: lmn/compiler/typechecker/statements/statement_dispatcher.py

import logging
from typing import Dict, Optional

# use mega unions
from lmn.compiler.ast.mega_union import Node
from lmn.compiler.typechecker.statements.break_statement_checker import BreakStatementChecker
from lmn.compiler.typechecker.statements.call_statement_checker import CallStatementChecker
from lmn.compiler.typechecker.statements.continue_statement_checker import ContinueStatementChecker
from lmn.compiler.typechecker.statements.for_statement_checker import ForStatementChecker

from .let_statement_checker import LetStatementChecker
from .assignment_statement_checker import AssignmentStatementChecker
from .return_statement_checker import ReturnStatementChecker
from .print_statement_checker import PrintStatementChecker
from .block_statement_checker import BlockStatementChecker
from .if_statement_checker import IfStatementChecker
from .function_definition_checker import FunctionDefinitionChecker

logger = logging.getLogger(__name__)

class StatementDispatcher:
    def __init__(self, symbol_table: Dict[str, str], expr_dispatcher):
        self.symbol_table = symbol_table
        self.expr_dispatcher = expr_dispatcher

    def check_statement(
        self,
        stmt: Node,
        local_scope: Dict[str, str] = None,
        function_return_type: Optional[str] = None   # <--- add this param
    ) -> Optional[str]:
        """
        Routes a statement to its checker based on stmt.type.
        If 'function_return_type' is provided, we pass it to ReturnStatementChecker
        so that 'return' statements unify with that type.
        Return value: some statements (like ReturnStatement) might produce a type.
        """
        old_table = self.symbol_table
        if local_scope is not None:
            self.symbol_table = local_scope

        try:
            stype = getattr(stmt, "type", None)
            logger.debug(f"Dispatching statement type: {stype}")

            if stype == "LetStatement":
                return LetStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "AssignmentStatement":
                return AssignmentStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "ReturnStatement":
                # We pass function_return_type here:
                return ReturnStatementChecker(self.symbol_table, self).check(
                    stmt,
                    local_scope,
                    function_return_type=function_return_type
                )

            elif stype == "PrintStatement":
                return PrintStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "BlockStatement":
                return BlockStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "IfStatement":
                return IfStatementChecker(self.symbol_table, self).check(stmt, local_scope)
            
            elif stype == "ForStatement":
                return ForStatementChecker(self.symbol_table, self).check(stmt, local_scope)
            
            elif stype == "BreakStatement":
                return BreakStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "ContinueStatement":
                return ContinueStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            
            elif stype == "CallStatement":
                return CallStatementChecker(self.symbol_table, self).check(stmt, local_scope)

            elif stype == "FunctionDefinition":
                return FunctionDefinitionChecker(self.symbol_table, self).check(stmt)

            else:
                logger.error(f"No checker available for statement type: {stype}")
                raise NotImplementedError(f"No checker available for statement type: {stype}")

        finally:
            if local_scope is not None:
                self.symbol_table = old_table

    def check_expression(
        self,
        expr: Node,
        target_type=None,
        local_scope: Dict[str, str] = None
    ):
        """
        Delegates to self.expr_dispatcher for expression type-checking.
        """
        old_table = self.symbol_table
        if local_scope is not None:
            self.symbol_table = local_scope

        try:
            return self.expr_dispatcher.check_expression(
                expr, target_type, local_scope=local_scope
            )
        finally:
            if local_scope is not None:
                self.symbol_table = old_table

# file: lmn/compiler/typechecker/statements/statement_dispatcher.py
import logging
from typing import Dict

# use mega unions
from lmn.compiler.ast.mega_union import Node

# Subclass-based checkers
from lmn.compiler.typechecker.statements.let_statement_checker import LetStatementChecker
from lmn.compiler.typechecker.statements.assignment_statement_checker import AssignmentStatementChecker
from lmn.compiler.typechecker.statements.return_statement_checker import ReturnStatementChecker
from lmn.compiler.typechecker.statements.print_statement_checker import PrintStatementChecker
from lmn.compiler.typechecker.statements.block_statement_checker import BlockStatementChecker
from lmn.compiler.typechecker.statements.if_statement_checker import IfStatementChecker
from lmn.compiler.typechecker.statements.function_definition_checker import FunctionDefinitionChecker

# logger
logger = logging.getLogger(__name__)

class StatementDispatcher:
    def __init__(self, symbol_table: Dict[str, str], expr_dispatcher):
        # Symbol table for variable lookup
        self.symbol_table = symbol_table
        self.expr_dispatcher = expr_dispatcher

    def check_statement(self, stmt: Node, local_scope: Dict[str, str] = None) -> None:
        """
        Routes a statement to its appropriate checker based on its type.
        If `local_scope` is provided, we temporarily override self.symbol_table
        while checking this statement (useful for block statements, function bodies, etc.).
        """
        old_table = self.symbol_table
        if local_scope is not None:
            self.symbol_table = local_scope

        try:
            stype = stmt.type
            logger.debug(f"Dispatching statement type: {stype}")

            if stype == "LetStatement":
                LetStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "AssignmentStatement":
                AssignmentStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "ReturnStatement":
                ReturnStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "PrintStatement":
                PrintStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "BlockStatement":
                BlockStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "IfStatement":
                IfStatementChecker(self.symbol_table, self).check(stmt)

            elif stype == "FunctionDefinition":
                FunctionDefinitionChecker(self.symbol_table, self).check(stmt)

            else:
                logger.error(f"No checker available for statement type: {stype}")
                raise NotImplementedError(f"No checker available for statement type: {stype}")

        finally:
            # revert to old table
            if local_scope is not None:
                self.symbol_table = old_table

    def check_expression(self, expr, hinted_type=None):
        """
        Typically delegates to self.expr_dispatcher for expression type-checking.
        """
        return self.expr_dispatcher.check_expression(expr, hinted_type)

# file: lmn/compiler/typechecker/statements/base_statement_checker.py
import logging
from typing import Dict

# logger
logger = logging.getLogger(__name__)

class BaseStatementChecker:
    def __init__(self, symbol_table: Dict[str, str], dispatcher: "StatementDispatcher"):
        # set symbol table and dispatcher
        self.symbol_table = symbol_table
        self.dispatcher = dispatcher

    def check(self, stmt) -> None:
        # not implemented
        raise NotImplementedError("This method should be implemented by subclasses.")

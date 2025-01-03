# file: lmn/compiler/typechecker/expressions/base_expression_checker.py
from ast import Dict, Expression
from typing import Optional

class BaseExpressionChecker:
    def __init__(self, dispatcher: "ExpressionDispatcher", symbol_table: Dict):
        self.dispatcher = dispatcher
        self.symbol_table = symbol_table

    def check(self, expr: Expression, target_type: Optional[str] = None) -> str:
        # not implemented yet
        raise NotImplementedError("This method should be implemented by subclasses.")

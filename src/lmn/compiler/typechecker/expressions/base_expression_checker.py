# file: lmn/compiler/typechecker/expressions/base_expression_checker.py
from typing import Optional, Dict, Any

class BaseExpressionChecker:
    def __init__(self, dispatcher: "ExpressionDispatcher", symbol_table: Dict[str, Any]):
        """
        :param dispatcher: A reference to the ExpressionDispatcher for sub-checks
        :param symbol_table: The global (or outer) symbol table
        """
        self.dispatcher = dispatcher
        self.symbol_table = symbol_table

    def check(
        self,
        expr: Any,                  # Typically an AST Expression node
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Perform type-checking on an expression, optionally using local_scope for lookups.
        Subclasses should override this method.

        :param expr: The AST expression node to check
        :param target_type: A hinted or expected type (e.g., for assignment)
        :param local_scope: A local scope dict if available, otherwise fallback to symbol_table
        :return: The inferred or unified type for this expression
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

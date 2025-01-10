import logging
from typing import Optional, Dict

# lmn imports
from lmn.compiler.ast import Expression
from lmn.compiler.ast.expressions.conversion_expression import ConversionExpression
from lmn.compiler.typechecker.expressions.array_literal_checker import ArrayLiteralChecker
from lmn.compiler.typechecker.expressions.assignment_checker import AssignmentChecker
from lmn.compiler.typechecker.expressions.binary_checker import BinaryChecker
from lmn.compiler.typechecker.expressions.conversion_expression_checker import ConversionExpressionChecker
from lmn.compiler.typechecker.expressions.fn_checker import FnChecker
from lmn.compiler.typechecker.expressions.json_literal_checker import JsonLiteralChecker
from lmn.compiler.typechecker.expressions.literal_checker import LiteralChecker
from lmn.compiler.typechecker.expressions.postfix_checker import PostfixChecker
from lmn.compiler.typechecker.expressions.unary_checker import UnaryChecker
from lmn.compiler.typechecker.expressions.variable_checker import VariableChecker

# Suppose you add a new checker:
from lmn.compiler.typechecker.expressions.anonymous_function_checker import AnonymousFunctionChecker

# Import your various AST expression classes
from lmn.compiler.ast.expressions.literal_expression import LiteralExpression
from lmn.compiler.ast.expressions.binary_expression import BinaryExpression
from lmn.compiler.ast.expressions.json_literal_expression import JsonLiteralExpression
from lmn.compiler.ast.expressions.array_literal_expression import ArrayLiteralExpression
from lmn.compiler.ast.expressions.variable_expression import VariableExpression
from lmn.compiler.ast.expressions.unary_expression import UnaryExpression
from lmn.compiler.ast.expressions.assignment_expression import AssignmentExpression
from lmn.compiler.ast.expressions.postfix_expression import PostfixExpression
from lmn.compiler.ast.expressions.fn_expression import FnExpression
from lmn.compiler.ast.expressions.anonymous_function_expression import AnonymousFunctionExpression

logger = logging.getLogger(__name__)

class ExpressionDispatcher:
    def __init__(self, symbol_table: Dict[str, str]):
        # Global or outer symbol table
        self.symbol_table = symbol_table

    def check_expression(
        self,
        expr: Expression,
        target_type: Optional[str] = None,
        local_scope: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Dispatch the given 'expr' node to the appropriate checker.
        If 'local_scope' is provided, it overrides the global symbol_table
        for this expression check. This helps with function or block-scoped variables.
        """
        # 1) Determine which scope we are using
        effective_scope = local_scope if local_scope is not None else self.symbol_table

        # 2) Debug logging
        expr_type_name = type(expr).__name__
        logger.debug(
            f"[ExpressionDispatcher] Checking expression of type='{expr_type_name}', "
            f"target_type='{target_type}'"
        )
        logger.debug(
            f"[ExpressionDispatcher] effective_scope keys = {list(effective_scope.keys())}"
        )

        # 3) Dispatch based on expression class
        if isinstance(expr, LiteralExpression):
            logger.debug("[ExpressionDispatcher] -> Using LiteralChecker")
            return LiteralChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, BinaryExpression):
            logger.debug("[ExpressionDispatcher] -> Using BinaryChecker")
            return BinaryChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, JsonLiteralExpression):
            logger.debug("[ExpressionDispatcher] -> Using JsonLiteralChecker")
            return JsonLiteralChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, ArrayLiteralExpression):
            logger.debug("[ExpressionDispatcher] -> Using ArrayLiteralChecker")
            return ArrayLiteralChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, VariableExpression):
            logger.debug("[ExpressionDispatcher] -> Using VariableChecker")
            # Notice we pass 'effective_scope' to the constructor => ensures local variables are recognized
            return VariableChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, UnaryExpression):
            logger.debug("[ExpressionDispatcher] -> Using UnaryChecker")
            return UnaryChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, AssignmentExpression):
            logger.debug("[ExpressionDispatcher] -> Using AssignmentChecker")
            return AssignmentChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, PostfixExpression):
            logger.debug("[ExpressionDispatcher] -> Using PostfixChecker")
            return PostfixChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, FnExpression):
            logger.debug("[ExpressionDispatcher] -> Using FnChecker")
            return FnChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, AnonymousFunctionExpression):
            logger.debug("[ExpressionDispatcher] -> Using AnonymousFunctionChecker")
            return AnonymousFunctionChecker(self, effective_scope).check(expr, target_type, local_scope)

        elif isinstance(expr, ConversionExpression):
            logger.debug("[ExpressionDispatcher] -> Using ConversionExpressionChecker")
            return ConversionExpressionChecker(self, effective_scope).check(expr, target_type, local_scope)

        else:
            logger.error(f"[ExpressionDispatcher] No checker for expression type='{expr_type_name}'")
            raise NotImplementedError(f"No checker available for {expr_type_name}.")
